from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.redis_client import get_redis
from backend.app.models.dict_info import DictInfo
from backend.app.models.dict_type import DictType
from backend.app.schemas.dict import (
    DictTypeCreateRequest,
    DictTypeDeleteRequest,
    DictTypeIdRequest,
    DictTypeOut,
    DictTypePageRequest,
    DictTypeUpdateRequest,
    PageResult,
    Pagination,
)

router = APIRouter(prefix="/dict/type", tags=["dict"])


def _key_page(dtype: DictType) -> str:
    return f"{dtype.key}_{dtype.page or 'undefined'}"


async def _invalidate(redis: Redis, dtype: DictType) -> None:
    await redis.delete(f"dict:data:{_key_page(dtype)}")


@router.post("/add")
async def add_type(
    payload: DictTypeCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    dtype = DictType(name=payload.name, key=payload.key, page=payload.page)
    session.add(dtype)
    await session.flush()
    await _invalidate(redis, dtype)
    return success(DictTypeOut(id=int(dtype.id), name=dtype.name, key=dtype.key, page=dtype.page))


@router.post("/update")
async def update_type(
    payload: DictTypeUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    result = await session.execute(select(DictType).where(DictType.id == payload.id))
    dtype = result.scalar_one_or_none()
    if not dtype:
        return business_error("字典类型不存在")

    old_key = _key_page(dtype)

    if payload.name is not None:
        dtype.name = payload.name
    if payload.key is not None:
        dtype.key = payload.key
    if payload.page is not None:
        dtype.page = payload.page

    await session.flush()

    await redis.delete(f"dict:data:{old_key}")
    await _invalidate(redis, dtype)

    return success(DictTypeOut(id=int(dtype.id), name=dtype.name, key=dtype.key, page=dtype.page))


@router.post("/delete")
async def delete_type(
    payload: DictTypeDeleteRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    ids = [int(i) for i in payload.ids]
    if not ids:
        return success(True)

    rows = (await session.execute(select(DictType).where(DictType.id.in_(ids)))).scalars().all()
    for dtype in rows:
        await _invalidate(redis, dtype)

    # Delete children first to satisfy FK constraint.
    await session.execute(DictInfo.__table__.delete().where(DictInfo.type_id.in_(ids)))
    await session.execute(DictType.__table__.delete().where(DictType.id.in_(ids)))
    await session.flush()
    return success(True)


@router.post("/info")
async def info_type(
    payload: DictTypeIdRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    result = await session.execute(select(DictType).where(DictType.id == payload.id))
    dtype = result.scalar_one_or_none()
    if not dtype:
        return success({})
    return success(DictTypeOut(id=int(dtype.id), name=dtype.name, key=dtype.key, page=dtype.page))


@router.post("/list")
async def list_type(
    payload: DictTypeIdRequest | DictTypePageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    # Accept flexible payloads (CRUD plugin may send different shapes).
    key = getattr(payload, "key", None)
    key_like = getattr(payload, "key_like", None)
    key_word = getattr(payload, "key_word", None)

    q = select(DictType)
    if key:
        q = q.where(DictType.key == key)
    if key_like:
        q = q.where(DictType.key.like(f"{key_like}%"))
    if key_word:
        q = q.where(DictType.name.ilike(f"%{key_word}%"))

    rows = (await session.execute(q.order_by(DictType.id.asc()))).scalars().all()
    return success([DictTypeOut(id=int(r.id), name=r.name, key=r.key, page=r.page) for r in rows])


@router.post("/page")
async def page_type(
    payload: DictTypePageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    page = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    q = select(DictType)
    cq = select(func.count()).select_from(DictType)

    if payload.key:
        q = q.where(DictType.key == payload.key)
        cq = cq.where(DictType.key == payload.key)
    if payload.key_like:
        q = q.where(DictType.key.like(f"{payload.key_like}%"))
        cq = cq.where(DictType.key.like(f"{payload.key_like}%"))
    if payload.key_word:
        q = q.where(DictType.name.ilike(f"%{payload.key_word}%"))
        cq = cq.where(DictType.name.ilike(f"%{payload.key_word}%"))

    total = (await session.execute(cq)).scalar_one()
    rows = (
        await session.execute(q.order_by(DictType.id.desc()).offset((page - 1) * size).limit(size))
    ).scalars().all()
    items = [DictTypeOut(id=int(r.id), name=r.name, key=r.key, page=r.page) for r in rows]
    return success(PageResult(list=items, pagination=Pagination(total=int(total), page=page, size=size)))


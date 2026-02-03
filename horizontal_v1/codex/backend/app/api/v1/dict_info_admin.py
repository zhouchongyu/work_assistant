from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import delete, func, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.redis_client import get_redis
from backend.app.models.dict_info import DictInfo
from backend.app.models.dict_type import DictType
from backend.app.schemas.dict import (
    DictInfoCreateRequest,
    DictInfoDeleteRequest,
    DictInfoIdRequest,
    DictInfoOut,
    DictInfoPageRequest,
    DictInfoUpdateRequest,
    PageResult,
    Pagination,
)

router = APIRouter(prefix="/dict/info", tags=["dict"])


def _key_page(dtype: DictType) -> str:
    return f"{dtype.key}_{dtype.page or 'undefined'}"


async def _invalidate(redis: Redis, session: AsyncSession, *, type_id: int) -> None:
    dtype = (await session.execute(select(DictType).where(DictType.id == type_id))).scalar_one_or_none()
    if not dtype:
        return
    await redis.delete(f"dict:data:{_key_page(dtype)}")


@router.post("/add")
async def add_info(
    payload: DictInfoCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    info = DictInfo(
        type_id=payload.type_id,
        name=payload.name,
        value=payload.value,
        order_num=payload.order_num,
        remark=payload.remark,
        parent_id=payload.parent_id,
        field_name=payload.field_name,
        is_show=payload.is_show,
        is_process=payload.is_process,
    )
    session.add(info)
    await session.flush()
    await _invalidate(redis, session, type_id=int(info.type_id))
    return success(
        DictInfoOut(
            id=int(info.id),
            type_id=int(info.type_id),
            name=info.name,
            value=info.value,
            order_num=int(info.order_num),
            remark=info.remark,
            parent_id=int(info.parent_id) if info.parent_id is not None else None,
            field_name=info.field_name,
            is_show=bool(info.is_show),
            is_process=bool(info.is_process),
        )
    )


@router.post("/update")
async def update_info(
    payload: DictInfoUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    info = (await session.execute(select(DictInfo).where(DictInfo.id == payload.id))).scalar_one_or_none()
    if not info:
        return business_error("字典项不存在")

    if payload.name is not None:
        info.name = payload.name
    if payload.value is not None:
        info.value = payload.value
    if payload.order_num is not None:
        info.order_num = payload.order_num
    if payload.remark is not None:
        info.remark = payload.remark
    if payload.parent_id is not None:
        info.parent_id = payload.parent_id
    if payload.field_name is not None:
        info.field_name = payload.field_name
    if payload.is_show is not None:
        info.is_show = payload.is_show
    if payload.is_process is not None:
        info.is_process = payload.is_process

    await session.flush()
    await _invalidate(redis, session, type_id=int(info.type_id))
    return success(DictInfoOut(id=int(info.id), type_id=int(info.type_id), name=info.name))


@router.post("/delete")
async def delete_info(
    payload: DictInfoDeleteRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    ids = [int(i) for i in payload.ids]
    if not ids:
        return success(True)

    cte = select(DictInfo.id).where(DictInfo.id.in_(ids)).cte(recursive=True)
    cte = cte.union_all(select(DictInfo.id).where(DictInfo.parent_id == cte.c.id))
    all_ids = [row[0] for row in (await session.execute(select(cte.c.id))).all()]

    type_ids = [
        row[0]
        for row in (
            await session.execute(select(DictInfo.type_id).where(DictInfo.id.in_(all_ids)).distinct())
        ).all()
    ]

    await session.execute(delete(DictInfo).where(DictInfo.id.in_(all_ids)))
    await session.flush()

    for type_id in type_ids:
        await _invalidate(redis, session, type_id=int(type_id))

    return success(True)


@router.post("/info")
async def info_dict_info(
    payload: DictInfoIdRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    info = (await session.execute(select(DictInfo).where(DictInfo.id == payload.id))).scalar_one_or_none()
    if not info:
        return success({})
    return success(
        DictInfoOut(
            id=int(info.id),
            type_id=int(info.type_id),
            name=info.name,
            value=info.value,
            order_num=int(info.order_num),
            remark=info.remark,
            parent_id=int(info.parent_id) if info.parent_id is not None else None,
            field_name=info.field_name,
            is_show=bool(info.is_show),
            is_process=bool(info.is_process),
        )
    )


@router.post("/page")
async def page_dict_info(
    payload: DictInfoPageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    page = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    q = select(DictInfo)
    cq = select(func.count()).select_from(DictInfo)

    if payload.type_id is not None:
        q = q.where(DictInfo.type_id == payload.type_id)
        cq = cq.where(DictInfo.type_id == payload.type_id)
    if payload.key_word:
        q = q.where(DictInfo.name.ilike(f"%{payload.key_word}%"))
        cq = cq.where(DictInfo.name.ilike(f"%{payload.key_word}%"))

    total = (await session.execute(cq)).scalar_one()
    rows = (
        await session.execute(q.order_by(DictInfo.order_num.asc(), DictInfo.id.asc()).offset((page - 1) * size).limit(size))
    ).scalars().all()
    items = [
        DictInfoOut(
            id=int(r.id),
            type_id=int(r.type_id),
            name=r.name,
            value=r.value,
            order_num=int(r.order_num),
            remark=r.remark,
            parent_id=int(r.parent_id) if r.parent_id is not None else None,
            field_name=r.field_name,
            is_show=bool(r.is_show),
            is_process=bool(r.is_process),
        )
        for r in rows
    ]
    return success(PageResult(list=items, pagination=Pagination(total=int(total), page=page, size=size)))


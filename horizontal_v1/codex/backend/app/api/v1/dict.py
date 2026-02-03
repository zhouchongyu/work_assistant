from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.redis_client import get_redis
from backend.app.models.dict_info import DictInfo
from backend.app.models.dict_type import DictType
from backend.app.schemas.dict import DictDataRequest, DictInfoItem

router = APIRouter(prefix="/dict", tags=["dict"])


def _as_number(value: str) -> int | float | str:
    try:
        num = float(value)
    except Exception:
        return value
    if num.is_integer():
        return int(num)
    return num


@router.post("/info/data")
async def dict_data(
    payload: DictDataRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current

    type_query = select(DictType)
    if payload.types:
        type_query = type_query.where(DictType.key.in_(payload.types))
    types = (await session.execute(type_query)).scalars().all()
    if not types:
        return success({})

    result: dict[str, list[dict]] = {}
    missing: list[tuple[DictType, str, str]] = []

    for t in types:
        page = t.page or "undefined"
        key = f"{t.key}_{page}"
        cache_key = f"dict:data:{key}"
        cached = await redis.get(cache_key)
        if cached:
            result[key] = json.loads(cached)
        else:
            missing.append((t, key, cache_key))

    if missing:
        missing_type_ids = [t.id for t, _, _ in missing]
        info_rows = (
            await session.execute(
                select(DictInfo)
                .where(DictInfo.type_id.in_(missing_type_ids))
                .order_by(asc(DictInfo.order_num), asc(DictInfo.created_at))
            )
        ).scalars()

        by_type: dict[int, list[DictInfo]] = {}
        for info in info_rows.all():
            by_type.setdefault(int(info.type_id), []).append(info)

        for t, key, cache_key in missing:
            items: list[dict] = []
            for info in by_type.get(int(t.id), []):
                val: int | float | str | None = info.value
                if isinstance(val, str) and val != "":
                    val = _as_number(val)

                items.append(
                    DictInfoItem(
                        id=int(info.id),
                        name=info.name,
                        type_id=int(info.type_id),
                        parent_id=int(info.parent_id) if info.parent_id is not None else None,
                        order_num=int(info.order_num),
                        value=val,
                        label=t.name,
                        key=key,
                        field_name=info.field_name,
                        is_show=bool(info.is_show),
                        is_process=bool(info.is_process),
                    ).model_dump(by_alias=True)
                )

            result[key] = items
            await redis.set(cache_key, json.dumps(items, ensure_ascii=False, separators=(",", ":")))

    return success(result)


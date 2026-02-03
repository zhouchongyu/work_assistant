from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_customer_column import RkCustomerColumn
from backend.app.schemas.rk_prefs import CustomerColumnDeleteRequest, CustomerColumnSetRequest

router = APIRouter(prefix="/rk/customer_column", tags=["rk"])


@router.get("/get_column_info")
async def get_column_info(
    name: str = Query(..., min_length=1, max_length=200),
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    owner_id = int(current.user.id)
    row = (
        await session.execute(
            select(RkCustomerColumn).where(
                RkCustomerColumn.owner_id == owner_id,
                RkCustomerColumn.name == name,
            )
        )
    ).scalar_one_or_none()

    if not row:
        return success(None)

    try:
        info = json.loads(row.column_info)
    except Exception:
        info = None

    return success(info)


@router.post("/set_column_info")
async def set_column_info(
    payload: CustomerColumnSetRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    owner_id = int(current.user.id)
    row = (
        await session.execute(
            select(RkCustomerColumn).where(
                RkCustomerColumn.owner_id == owner_id,
                RkCustomerColumn.name == payload.name,
            )
        )
    ).scalar_one_or_none()

    data = json.dumps(payload.info, ensure_ascii=False, separators=(",", ":"))
    if not row:
        row = RkCustomerColumn(
            owner_id=owner_id,
            name=payload.name,
            column_info=data,
            created_by=owner_id,
            updated_by=owner_id,
            department_id=current.user.department_id,
            active=True,
            to_be_confirmed=False,
        )
        session.add(row)
        await session.flush()
        return success(True)

    row.column_info = data
    row.updated_by = owner_id
    await session.flush()
    return success(True)


@router.post("/delete_column_info")
async def delete_column_info(
    payload: CustomerColumnDeleteRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    owner_id = int(current.user.id)
    await session.execute(
        delete(RkCustomerColumn).where(
            RkCustomerColumn.owner_id == owner_id,
            RkCustomerColumn.name == payload.name,
        )
    )
    await session.flush()
    return success(True)


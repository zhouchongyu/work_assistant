from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_customer import RkCustomer
from backend.app.schemas.rk_customer import (
    PageRequest,
    PageResult,
    Pagination,
    RkCustomerCreateRequest,
    RkCustomerOut,
    RkCustomerUpdateRequest,
)

router = APIRouter(prefix="/rk/customer", tags=["rk"])


@router.post("/add")
async def add_customer(
    payload: RkCustomerCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    customer = RkCustomer(
        name=payload.name,
        code=payload.code,
        created_by=int(current.user.id),
        updated_by=int(current.user.id),
        owner_id=int(current.user.id),
        department_id=current.user.department_id,
        active=True,
        to_be_confirmed=False,
    )
    session.add(customer)
    await session.flush()
    return success(RkCustomerOut(id=int(customer.id), name=customer.name, code=customer.code))


@router.post("/update")
async def update_customer(
    payload: RkCustomerUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    result = await session.execute(select(RkCustomer).where(RkCustomer.id == payload.id))
    customer = result.scalar_one_or_none()
    if not customer:
        return business_error("客户不存在")

    if payload.name is not None:
        customer.name = payload.name
    if payload.code is not None:
        customer.code = payload.code
    customer.updated_by = int(current.user.id)
    await session.flush()

    return success(RkCustomerOut(id=int(customer.id), name=customer.name, code=customer.code))


@router.post("/page")
async def page_customers(
    payload: PageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    page = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    filters = []
    if payload.active_switch:
        filters.append(RkCustomer.active.is_(True))

    total = (
        await session.execute(select(func.count()).select_from(RkCustomer).where(*filters))
    ).scalar_one()

    rows = (
        await session.execute(
            select(RkCustomer)
            .where(*filters)
            .order_by(RkCustomer.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    ).scalars().all()

    items = [RkCustomerOut(id=int(r.id), name=r.name, code=r.code) for r in rows]

    return success(
        PageResult(
            list=items,
            pagination=Pagination(total=int(total), page=page, size=size),
        )
    )

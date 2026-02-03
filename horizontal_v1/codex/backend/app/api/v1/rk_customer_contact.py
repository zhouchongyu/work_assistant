from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_customer_contact import RkCustomerContact
from backend.app.schemas.rk_vendor import (
    RkCustomerContactCreateRequest,
    RkCustomerContactOut,
    RkCustomerContactUpdateRequest,
)

router = APIRouter(prefix="/rk/customer_contact", tags=["rk"])


@router.get("/list")
async def list_customer_contacts(
    customer_id: int = Query(..., alias="customerId", ge=1),
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    rows = (
        await session.execute(
            select(RkCustomerContact)
            .where(RkCustomerContact.customer_id == customer_id)
            .order_by(asc(RkCustomerContact.id))
        )
    ).scalars().all()
    return success(
        [
            RkCustomerContactOut(
                id=int(r.id),
                customer_id=int(r.customer_id),
                name=r.name,
                email=r.email,
                phone=r.phone,
                default=r.is_default,
            )
            for r in rows
        ]
    )


@router.post("/add")
async def add_customer_contact(
    payload: RkCustomerContactCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    contact = RkCustomerContact(
        customer_id=payload.customer_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        is_default=payload.default,
        created_by=int(current.user.id),
        updated_by=int(current.user.id),
        owner_id=int(current.user.id),
        department_id=current.user.department_id,
        active=True,
        to_be_confirmed=False,
    )
    session.add(contact)
    await session.flush()
    return success(
        RkCustomerContactOut(
            id=int(contact.id),
            customer_id=int(contact.customer_id),
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            default=contact.is_default,
        )
    )


@router.post("/update")
async def update_customer_contact(
    payload: RkCustomerContactUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await session.execute(select(RkCustomerContact).where(RkCustomerContact.id == payload.id))
    contact = result.scalar_one_or_none()
    if not contact:
        return success(False)

    contact.customer_id = payload.customer_id
    if payload.name is not None:
        contact.name = payload.name
    if payload.email is not None:
        contact.email = payload.email
    if payload.phone is not None:
        contact.phone = payload.phone
    if payload.default is not None:
        contact.is_default = payload.default
    contact.updated_by = int(current.user.id)
    await session.flush()
    return success(True)


from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_vendor_contact import RkVendorContact
from backend.app.schemas.rk_vendor import (
    RkVendorContactCreateRequest,
    RkVendorContactOut,
    RkVendorContactUpdateRequest,
)

router = APIRouter(prefix="/rk/vendor_contact", tags=["rk"])


@router.get("/list")
async def list_vendor_contacts(
    vendor_id: int = Query(..., alias="vendorId", ge=1),
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    _ = current
    rows = (
        await session.execute(
            select(RkVendorContact).where(RkVendorContact.vendor_id == vendor_id).order_by(asc(RkVendorContact.id))
        )
    ).scalars().all()
    return success(
        [
            RkVendorContactOut(
                id=int(r.id),
                vendor_id=int(r.vendor_id),
                name=r.name,
                email=r.email,
                phone=r.phone,
                default=r.is_default,
            )
            for r in rows
        ]
    )


@router.post("/add")
async def add_vendor_contact(
    payload: RkVendorContactCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    contact = RkVendorContact(
        vendor_id=payload.vendor_id,
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
        RkVendorContactOut(
            id=int(contact.id),
            vendor_id=int(contact.vendor_id),
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            default=contact.is_default,
        )
    )


@router.post("/update")
async def update_vendor_contact(
    payload: RkVendorContactUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await session.execute(select(RkVendorContact).where(RkVendorContact.id == payload.id))
    contact = result.scalar_one_or_none()
    if not contact:
        return success(False)

    contact.vendor_id = payload.vendor_id
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


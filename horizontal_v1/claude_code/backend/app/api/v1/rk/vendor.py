"""
Vendor API endpoints.

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/vendor.ts (if exists)
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.vendor import vendor_service

router = APIRouter(prefix="/vendor", tags=["Vendor"])


@router.post("/add", response_model=None)
async def add_vendor(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new vendor."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id
        data["ownerId"] = user_id

    result = await vendor_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_vendor(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete vendors by IDs (soft delete)."""
    for vendor_id in ids:
        await vendor_service.delete(db, vendor_id)
    return success()


@router.post("/update", response_model=None)
async def update_vendor(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a vendor record."""
    vendor_id = data.pop("id", None)
    if not vendor_id:
        return success(result=None)

    await vendor_service.update(db, vendor_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_vendor_info(
    id: int = Query(..., description="Vendor ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get vendor by ID."""
    result = await vendor_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_vendors(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List all vendors."""
    result = await vendor_service.list_with_pagination(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_vendors(
    page: int = 1,
    size: int = 20,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get vendors with pagination."""
    result = await vendor_service.list_with_pagination(db, page=page, size=size)
    return success(result=result)


# ==================== Vendor Contact ====================


@router.post("/contact/add", response_model=None)
async def add_vendor_contact(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new vendor contact."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id

    result = await vendor_service.create_contact(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/contact/delete", response_model=None)
async def delete_vendor_contact(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete vendor contacts by IDs."""
    for contact_id in ids:
        await vendor_service.delete_contact(db, contact_id)
    return success()


@router.post("/contact/update", response_model=None)
async def update_vendor_contact(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a vendor contact."""
    contact_id = data.pop("id", None)
    if not contact_id:
        return success(result=None)

    await vendor_service.update_contact(db, contact_id, data)
    return success()


@router.post("/contact/list", response_model=None)
async def list_vendor_contacts(
    vendorId: int = Query(..., description="Vendor ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List contacts for a vendor."""
    result = await vendor_service.get_contacts_by_vendor(db, vendorId)
    return success(result=[to_dict(c) for c in result])

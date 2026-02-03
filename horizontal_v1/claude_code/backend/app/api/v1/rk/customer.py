"""
Customer API endpoints.

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/customer.ts
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.customer import customer_service

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/add", response_model=None)
async def add_customer(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new customer."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id
        data["ownerId"] = user_id

    result = await customer_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_customer(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete customers by IDs (soft delete)."""
    for customer_id in ids:
        await customer_service.delete(db, customer_id)
    return success()


@router.post("/update", response_model=None)
async def update_customer(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a customer record."""
    customer_id = data.pop("id", None)
    if not customer_id:
        return success(result=None)

    await customer_service.update(db, customer_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_customer_info(
    id: int = Query(..., description="Customer ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get customer by ID."""
    result = await customer_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_customers(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List all customers."""
    result = await customer_service.list_with_pagination(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_customers(
    page: int = 1,
    size: int = 20,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get customers with pagination."""
    result = await customer_service.list_with_pagination(db, page=page, size=size)
    return success(result=result)


# ==================== Customer Contact ====================


@router.post("/contact/add", response_model=None)
async def add_customer_contact(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new customer contact."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id

    result = await customer_service.create_contact(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/contact/delete", response_model=None)
async def delete_customer_contact(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete customer contacts by IDs."""
    for contact_id in ids:
        await customer_service.delete_contact(db, contact_id)
    return success()


@router.post("/contact/update", response_model=None)
async def update_customer_contact(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a customer contact."""
    contact_id = data.pop("id", None)
    if not contact_id:
        return success(result=None)

    await customer_service.update_contact(db, contact_id, data)
    return success()


@router.post("/contact/list", response_model=None)
async def list_customer_contacts(
    customerId: int = Query(..., description="Customer ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List contacts for a customer."""
    result = await customer_service.get_contacts_by_customer(db, customerId)
    return success(result=[to_dict(c) for c in result])

"""
Supply (Resume) API endpoints.

Reference:
- assistant_py/app/v1/controller/supplyController.py
- cool-admin-midway/src/modules/rk/controller/admin/supply.ts
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.supply import supply_service

router = APIRouter(prefix="/supply", tags=["Supply"])


@router.post("/add", response_model=None)
async def add_supply(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new supply record."""
    # Add creator info from request state
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id
        data["ownerId"] = user_id

    result = await supply_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_supply(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete supplies by IDs (soft delete)."""
    for supply_id in ids:
        await supply_service.delete(db, supply_id)
    return success()


@router.post("/update", response_model=None)
async def update_supply(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a supply record."""
    supply_id = data.pop("id", None)
    if not supply_id:
        return success(result=None)

    await supply_service.update(db, supply_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_supply_info(
    id: int = Query(..., description="Supply ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get supply by ID."""
    result = await supply_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_supplies(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List all supplies."""
    result = await supply_service.list_with_pagination(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_supplies(
    page: int = 1,
    size: int = 20,
    vendorId: int | None = None,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get supplies with pagination."""
    conditions = {}
    if vendorId is not None:
        conditions["vendorId"] = vendorId

    result = await supply_service.list_with_pagination(
        db, page=page, size=size, conditions=conditions if conditions else None
    )
    return success(result=result)


@router.post("/ai", response_model=None)
async def get_supply_ai(
    id: int = Query(..., description="Supply ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get supply AI data."""
    result = await supply_service.get_ai_data(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/editRecords", response_model=None)
async def get_edit_records(
    id: int = Query(..., description="Supply ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get supply edit records."""
    result = await supply_service.get_edit_records(db, id)
    return success(result=[to_dict(r) for r in result])

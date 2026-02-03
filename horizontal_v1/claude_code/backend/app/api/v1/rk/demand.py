"""
Demand API endpoints.

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/demand.ts
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.demand import demand_service

router = APIRouter(prefix="/demand", tags=["Demand"])


@router.post("/add", response_model=None)
async def add_demand(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new demand record."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id
        data["ownerId"] = user_id

    result = await demand_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_demand(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete demands by IDs (soft delete)."""
    for demand_id in ids:
        await demand_service.delete(db, demand_id)
    return success()


@router.post("/update", response_model=None)
async def update_demand(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a demand record."""
    demand_id = data.pop("id", None)
    if not demand_id:
        return success(result=None)

    await demand_service.update(db, demand_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_demand_info(
    id: int = Query(..., description="Demand ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get demand by ID."""
    result = await demand_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_demands(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List all demands."""
    result = await demand_service.list_with_pagination(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_demands(
    page: int = 1,
    size: int = 20,
    customerId: int | None = None,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get demands with pagination."""
    conditions = {}
    if customerId is not None:
        conditions["customerId"] = customerId

    result = await demand_service.list_with_pagination(
        db, page=page, size=size, conditions=conditions if conditions else None
    )
    return success(result=result)


@router.post("/ai", response_model=None)
async def get_demand_ai(
    id: int = Query(..., description="Demand ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get demand AI data."""
    result = await demand_service.get_ai_data(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/conditions", response_model=None)
async def get_demand_conditions(
    id: int = Query(..., description="Demand ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get demand conditions."""
    result = await demand_service.get_conditions(db, id)
    return success(result=[to_dict(c) for c in result])

"""
Case (Supply-Demand Link) API endpoints.

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/supply_demand_link.ts
"""

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.case import case_service

router = APIRouter(prefix="/supply_demand_link", tags=["Case"])


@router.post("/add", response_model=None)
async def add_case(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new case."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id
        data["ownerId"] = user_id

    result = await case_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_case(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete cases by IDs (soft delete)."""
    for case_id in ids:
        await case_service.delete(db, case_id)
    return success()


@router.post("/update", response_model=None)
async def update_case(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update a case record."""
    case_id = data.pop("id", None)
    if not case_id:
        return success(result=None)

    await case_service.update(db, case_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_case_info(
    id: int = Query(..., description="Case ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get case by ID."""
    result = await case_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_cases(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """List all cases."""
    result = await case_service.list_with_pagination(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_cases(
    page: int = 1,
    size: int = 20,
    supplyId: int | None = None,
    demandId: int | None = None,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get cases with pagination."""
    conditions = {}
    if supplyId is not None:
        conditions["supplyId"] = supplyId
    if demandId is not None:
        conditions["demandId"] = demandId

    result = await case_service.list_with_pagination(
        db, page=page, size=size, conditions=conditions if conditions else None
    )
    return success(result=result)


@router.post("/updateStatus", response_model=None)
async def update_case_status(
    id: int = Body(...),
    status: str = Body(...),
    remark: str | None = Body(default=None),
    force: bool = Body(default=False),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Update case status."""
    await case_service.update_status(db, id, status, remark, force)
    return success()


@router.post("/statusHistory", response_model=None)
async def get_status_history(
    id: int = Query(..., description="Case ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get case status history."""
    result = await case_service.get_status_history(db, id)
    return success(result=[to_dict(s) for s in result])


@router.post("/matchResult", response_model=None)
async def get_match_result(
    supplyId: int = Query(...),
    demandId: int = Query(...),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get match result for supply-demand pair."""
    result = await case_service.get_match_result(db, supplyId, demandId)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/matchResults", response_model=None)
async def get_match_results_by_demand(
    demandId: int = Query(...),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get all match results for a demand."""
    result = await case_service.get_match_results_by_demand(db, demandId)
    return success(result=[to_dict(m) for m in result])

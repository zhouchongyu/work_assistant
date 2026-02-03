"""
System parameter API endpoints.

Provides CRUD operations for system parameters.

Reference:
- cool-admin-midway/src/modules/base/controller/admin/sys/param.ts
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.param import param_service

router = APIRouter(prefix="/param", tags=["SysParam"])


@router.post("/add", response_model=None)
async def add_param(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Create a new system parameter.
    """
    result = await param_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_param(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Delete system parameters by IDs.
    """
    for param_id in ids:
        await param_service.delete(db, param_id)
    return success()


@router.post("/update", response_model=None)
async def update_param(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Update a system parameter.
    """
    param_id = data.pop("id", None)
    if not param_id:
        return success(result=None)

    await param_service.update(db, param_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_param_info(
    id: int = Query(..., description="Parameter ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get system parameter by ID.
    """
    result = await param_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/page", response_model=None)
async def page_params(
    page: int = 1,
    size: int = 20,
    keyWord: str | None = None,
    dataType: int | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get system parameters with pagination.
    """
    result = await param_service.list_with_pagination(
        db, page=page, size=size, keyword=keyWord, data_type=dataType
    )
    return success(result=result)


@router.get("/html", response_class=HTMLResponse)
async def get_html_by_key(
    key: str = Query(..., description="Parameter key"),
    db: AsyncSession = Depends(get_async_session),
) -> str:
    """
    Get HTML page content by parameter key.

    Used for rendering rich text parameters as HTML page.
    """
    return await param_service.get_html_by_key(db, key)

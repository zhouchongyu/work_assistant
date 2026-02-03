"""
Operation log API endpoints.

Provides log viewing and management.

Reference:
- cool-admin-midway/src/modules/base/controller/admin/sys/log.ts
"""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.services.log import log_service

router = APIRouter(prefix="/log", tags=["SysLog"])


@router.post("/page", response_model=None)
async def page_logs(
    page: int = 1,
    size: int = 20,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get operation logs with pagination.
    """
    result = await log_service.list_with_pagination(
        db, page=page, size=size, keyword=keyWord
    )
    return success(result=result)


@router.post("/clear", response_model=None)
async def clear_logs(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Clear all operation logs.
    """
    await log_service.clear(db, clear_all=True)
    return success()


@router.post("/setKeep", response_model=None)
async def set_keep_days(
    value: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Set log retention period in days.
    """
    await log_service.set_keep_days(db, value)
    return success()


@router.get("/getKeep", response_model=None)
async def get_keep_days(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get log retention period in days.
    """
    days = await log_service.get_keep_days(db)
    return success(result=days)

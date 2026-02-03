"""
Notice API endpoints.

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/notice.ts
"""

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.services.rk.notice import notice_service

router = APIRouter(prefix="/notice", tags=["Notice"])


@router.post("/add", response_model=None)
async def add_notice(
    data: dict,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Create a new notice."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        data["createdBy"] = user_id

    result = await notice_service.create(db, data)
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_notice(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Delete notices by IDs."""
    for notice_id in ids:
        await notice_service.delete(db, notice_id)
    return success()


@router.post("/info", response_model=None)
async def get_notice_info(
    id: int = Query(..., description="Notice ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get notice by ID."""
    result = await notice_service.get_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/page", response_model=None)
async def page_notices(
    page: int = 1,
    size: int = 20,
    unreadOnly: bool = False,
    request: Request = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get notices with pagination for current user."""
    user_id = getattr(request.state, "user_id", None) if request else None
    if not user_id:
        return success(result={"list": [], "pagination": {"page": page, "size": size, "total": 0}})

    result = await notice_service.list_by_receiver(
        db, user_id, page=page, size=size, unread_only=unreadOnly
    )
    return success(result=result)


@router.post("/markRead", response_model=None)
async def mark_as_read(
    id: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Mark a notice as read."""
    await notice_service.mark_as_read(db, id)
    return success()


@router.post("/markAllRead", response_model=None)
async def mark_all_as_read(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Mark all notices as read for current user."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        await notice_service.mark_all_as_read(db, user_id)
    return success()


@router.get("/unreadCount", response_model=None)
async def get_unread_count(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """Get unread notice count for current user."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return success(result=0)

    count = await notice_service.get_unread_count(db, user_id)
    return success(result=count)

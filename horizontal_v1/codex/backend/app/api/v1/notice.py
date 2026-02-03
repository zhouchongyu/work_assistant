from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_notice import RkNotice
from backend.app.schemas.notice import NoticeMarkReadRequest, NoticeOut, NoticePageRequest, NoticePageResult, Pagination

router = APIRouter(prefix="/notice", tags=["notice"])


@router.get("/unread_count")
async def unread_count(
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    filters = [RkNotice.active.is_(True), RkNotice.is_read.is_(False)]
    if current.user.username != "admin":
        filters.append(RkNotice.receiver_id == int(current.user.id))

    total = (await session.execute(select(func.count()).select_from(RkNotice).where(*filters))).scalar_one()
    return success(int(total))


@router.post("/page")
async def page(
    payload: NoticePageRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    page_num = max(1, int(payload.page))
    size = min(200, max(1, int(payload.size)))

    filters = [RkNotice.active.is_(True)]
    if current.user.username != "admin":
        filters.append(RkNotice.receiver_id == int(current.user.id))
    if payload.is_read is not None:
        filters.append(RkNotice.is_read.is_(bool(payload.is_read)))

    total = (await session.execute(select(func.count()).select_from(RkNotice).where(*filters))).scalar_one()
    rows = (
        await session.execute(
            select(RkNotice)
            .where(*filters)
            .order_by(RkNotice.id.desc())
            .offset((page_num - 1) * size)
            .limit(size)
        )
    ).scalars().all()

    items = [
        NoticeOut(
            id=int(r.id),
            content=r.content,
            is_read=bool(r.is_read),
            type=r.type,
            model=r.model,
            created_at=r.created_at,
        )
        for r in rows
    ]

    return success(
        NoticePageResult(
            list=items,
            pagination=Pagination(total=int(total), page=page_num, size=size),
        )
    )


@router.post("/mark_read")
async def mark_read(
    payload: NoticeMarkReadRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not payload.ids:
        return success(None)

    stmt = update(RkNotice).where(RkNotice.id.in_(payload.ids))
    if current.user.username != "admin":
        stmt = stmt.where(RkNotice.receiver_id == int(current.user.id))
    stmt = stmt.values(is_read=True)

    await session.execute(stmt)
    return success(None)


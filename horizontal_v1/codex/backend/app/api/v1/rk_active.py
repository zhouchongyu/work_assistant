from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.models.rk_active import RkActive
from backend.app.schemas.rk_prefs import ActiveSwitchOut, ActiveSwitchSetRequest

router = APIRouter(prefix="/rk/active", tags=["rk"])


@router.get("/get_switch")
async def get_switch(
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    user_id = int(current.user.id)
    row = (await session.execute(select(RkActive).where(RkActive.user_id == user_id))).scalar_one_or_none()
    if not row:
        return success(ActiveSwitchOut(status=False))
    return success(ActiveSwitchOut(status=bool(row.status)))


@router.post("/active_switch")
async def set_switch(
    payload: ActiveSwitchSetRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    user_id = int(current.user.id)
    row = (await session.execute(select(RkActive).where(RkActive.user_id == user_id))).scalar_one_or_none()
    if not row:
        row = RkActive(user_id=user_id, status=bool(payload.status))
        session.add(row)
        await session.flush()
        return success(ActiveSwitchOut(status=bool(row.status)))

    row.status = bool(payload.status)
    await session.flush()
    return success(ActiveSwitchOut(status=bool(row.status)))


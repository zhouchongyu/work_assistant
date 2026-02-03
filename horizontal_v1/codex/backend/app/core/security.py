from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.settings import get_settings
from backend.app.db.deps import get_db_session
from backend.app.models.sys_user import SysUser
from backend.app.models.sys_user_role import SysUserRole
from backend.app.services.auth_service import decode_token


@dataclass(frozen=True)
class CurrentUser:
    user: SysUser
    role_ids: list[int]


def _extract_token(request: Request) -> str | None:
    raw = request.headers.get("Authorization")
    if not raw:
        return None
    if raw.startswith("Bearer "):
        return raw.removeprefix("Bearer ").strip() or None
    return raw.strip() or None


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUser:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    settings = get_settings()
    try:
        payload = decode_token(token, settings=settings)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if payload.get("isRefresh"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = payload.get("userId")
    password_version = payload.get("passwordVersion")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    result = await session.execute(select(SysUser).where(SysUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.status == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if password_version != user.password_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    role_result = await session.execute(
        select(SysUserRole.role_id).where(SysUserRole.user_id == user_id)
    )
    role_ids = [row[0] for row in role_result.all()]

    return CurrentUser(user=user, role_ids=role_ids)


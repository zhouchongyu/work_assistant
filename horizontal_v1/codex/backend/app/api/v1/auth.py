from __future__ import annotations

import base64
import io
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from PIL import Image, ImageDraw, ImageFont
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.core.settings import get_settings
from backend.app.db.deps import get_db_session
from backend.app.integrations.redis_client import get_redis
from backend.app.models.sys_user import SysUser
from backend.app.models.sys_user_role import SysUserRole
from backend.app.schemas.auth import (
    CaptchaResponse,
    LoginRequest,
    MeResponse,
    RefreshTokenRequest,
    TokenPair,
)
from backend.app.services.auth_service import decode_token, encode_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _generate_captcha_code(length: int = 4) -> str:
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _build_captcha_png(text: str, *, width: int, height: int) -> bytes:
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    text_width = draw.textlength(text, font=font)
    x = max(0, int((width - text_width) // 2))
    y = max(0, int((height - 12) // 2))

    draw.text((x, y), text, fill="#2c3142", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@router.get("/captcha")
async def captcha(
    redis: Redis = Depends(get_redis),
    type: str = Query(default="base64"),
    width: int = Query(default=150),
    height: int = Query(default=45),
):
    captcha_id = str(uuid.uuid4())
    code = _generate_captcha_code()

    png_bytes = _build_captcha_png(code, width=width, height=height)
    data_b64 = base64.b64encode(png_bytes).decode("ascii")
    data = f"data:image/png;base64,{data_b64}"

    await redis.set(f"verify:img:{captcha_id}", code.lower(), ex=1800)
    return success(CaptchaResponse(captcha_id=captcha_id, data=data))


@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    captcha_key = f"verify:img:{payload.captcha_id}"
    expected = await redis.get(captcha_key)
    if not expected or expected != payload.verify_code.lower():
        return business_error("验证码不正确")
    await redis.delete(captcha_key)

    result = await session.execute(select(SysUser).where(SysUser.username == payload.username))
    user = result.scalar_one_or_none()
    if not user or user.status == 0:
        return business_error("账户或密码不正确~")

    if not verify_password(payload.password, user.password_hash):
        return business_error("账户或密码不正确~")

    role_result = await session.execute(
        select(SysUserRole.role_id).where(SysUserRole.user_id == user.id)
    )
    role_ids = [row[0] for row in role_result.all()]
    if not role_ids:
        return business_error("该用户未设置任何角色，无法登录~")

    settings = get_settings()
    token_payload = {
        "isRefresh": False,
        "userId": int(user.id),
        "username": user.username,
        "roleIds": role_ids,
        "passwordVersion": user.password_version,
        "departmentId": user.department_id,
        "nickName": user.nick_name,
    }
    access_token = encode_token(
        token_payload, settings=settings, expires_in_seconds=settings.access_token_expire_seconds
    )
    refresh_token = encode_token(
        {**token_payload, "isRefresh": True},
        settings=settings,
        expires_in_seconds=settings.refresh_token_expire_seconds,
    )

    return success(
        TokenPair(
            token=access_token,
            expire=settings.access_token_expire_seconds,
            refresh_token=refresh_token,
            refresh_expire=settings.refresh_token_expire_seconds,
        )
    )


@router.post("/refresh-token")
async def refresh_token(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    settings = get_settings()
    try:
        decoded = decode_token(payload.refresh_token, settings=settings)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not decoded.get("isRefresh"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = decoded.get("userId")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    result = await session.execute(select(SysUser).where(SysUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.status == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if decoded.get("passwordVersion") != user.password_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    role_result = await session.execute(
        select(SysUserRole.role_id).where(SysUserRole.user_id == user.id)
    )
    role_ids = [row[0] for row in role_result.all()]
    if not role_ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token_payload = {
        "isRefresh": False,
        "userId": int(user.id),
        "username": user.username,
        "roleIds": role_ids,
        "passwordVersion": user.password_version,
        "departmentId": user.department_id,
        "nickName": user.nick_name,
    }
    access_token = encode_token(
        token_payload, settings=settings, expires_in_seconds=settings.access_token_expire_seconds
    )
    refresh_token_new = encode_token(
        {**token_payload, "isRefresh": True},
        settings=settings,
        expires_in_seconds=settings.refresh_token_expire_seconds,
    )

    return success(
        TokenPair(
            token=access_token,
            expire=settings.access_token_expire_seconds,
            refresh_token=refresh_token_new,
            refresh_expire=settings.refresh_token_expire_seconds,
        )
    )


@router.post("/logout")
async def logout():
    return success(None)


@router.get("/me")
async def me(current: CurrentUser = Depends(get_current_user)):
    user = current.user
    return success(
        MeResponse(
            id=int(user.id),
            username=user.username,
            name=user.name,
            nick_name=user.nick_name,
            department_id=user.department_id,
            role_id_list=[int(rid) for rid in current.role_ids],
        )
    )


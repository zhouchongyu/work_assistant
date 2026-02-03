"""
Open API endpoints (no authentication required).

Includes login, captcha, and other public endpoints.

Reference:
- cool-admin-midway/src/modules/base/controller/admin/open.ts
- Wiki: API参考文档/API参考文档.md
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.schemas.auth import (
    CaptchaResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/open", tags=["Open"])


@router.get("/captcha", response_model=None)
async def get_captcha(
    type: str = Query("base64", description="Captcha type: base64, svg"),
    width: int = Query(150, description="Captcha width"),
    height: int = Query(50, description="Captcha height"),
) -> SuccessResponse:
    """
    Get captcha image for login.

    Returns captchaId and image data (base64 or SVG).
    """
    result = await auth_service.generate_captcha(captcha_type=type)
    return success(result=result.model_dump(by_alias=True))


@router.post("/login", response_model=None)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    User login.

    Validates captcha, username/password, and returns JWT tokens.
    """
    result = await auth_service.login(
        username=data.username,
        password=data.password,
        captcha_id=data.captcha_id,
        verify_code=data.verify_code,
        db=db,
    )
    return success(result=result.model_dump(by_alias=True))


@router.post("/refreshToken", response_model=None)
async def refresh_token(data: RefreshTokenRequest) -> SuccessResponse:
    """
    Refresh access token using refresh token.

    Returns new access token and refresh token.
    """
    result = await auth_service.refresh_token(data.refresh_token)
    return success(result=result.model_dump(by_alias=True))


@router.get("/eps", response_model=None)
async def get_eps() -> SuccessResponse:
    """
    Get EPS (Entity Permission Schema) data.

    This endpoint is kept for backward compatibility but returns empty data
    since V2 uses explicit API client instead of EPS.
    """
    return success(result=[])

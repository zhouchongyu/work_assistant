from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse, SmsCodeRequest, CaptchaResponse
from app.services.auth import create_access_token, create_refresh_token, verify_token, AuthService
from app.core.exceptions import BusinessError, UnauthorizedError
from app.core.config.settings import settings


router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    user_info = await AuthService.authenticate_user(request.phone, request.password)
    if not user_info:
        raise BusinessError(message="用户名或密码错误", code=1001)

    # 生成令牌
    access_token = create_access_token(
        data={"sub": request.phone, "user_id": user_info["id"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": request.phone, "user_id": user_info["id"]}
    )

    return LoginResponse(
        code=1000,
        message="success",
        access_token=access_token,
        refresh_token=refresh_token,
        user_info=user_info
    )


@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """刷新访问令牌"""
    payload = verify_token(request.refresh_token)
    if payload and payload.get("type") == "refresh":
        # 生成新的访问令牌
        new_access_token = create_access_token(
            data={"sub": payload.get("sub"), "user_id": payload.get("user_id")}
        )

        return RefreshTokenResponse(
            code=1000,
            message="success",
            access_token=new_access_token
        )
    else:
        raise UnauthorizedError(message="无效的刷新令牌")


@router.post("/sms-code", response_model=dict)
async def sms_code(request: SmsCodeRequest):
    """获取短信验证码"""
    # 这里应该实现短信验证码逻辑
    # 为了演示，我们返回成功
    return {"code": 1000, "message": "短信验证码已发送"}


@router.get("/captcha", response_model=CaptchaResponse)
async def captcha():
    """获取图片验证码"""
    # 这里应该生成验证码图片
    # 为了演示，我们返回模拟数据
    return CaptchaResponse(
        code=1000,
        message="success",
        captcha_id=str(uuid.uuid4()),
        img="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth"}


# 用于保护需要认证的路由的依赖
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    user_info = await AuthService.get_user_by_token(token)
    if user_info is None:
        raise UnauthorizedError(message="无效的访问令牌")

    return user_info
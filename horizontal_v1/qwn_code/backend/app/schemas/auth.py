from app.schemas.response import BaseSchema
from typing import Optional


class LoginRequest(BaseSchema):
    """登录请求模型"""
    phone: str
    password: str


class LoginResponse(BaseSchema):
    """登录响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_info: Optional[dict] = None


class RefreshTokenRequest(BaseSchema):
    """刷新令牌请求模型"""
    refresh_token: str


class RefreshTokenResponse(BaseSchema):
    """刷新令牌响应模型"""
    access_token: str
    token_type: str = "bearer"


class SmsCodeRequest(BaseSchema):
    """短信验证码请求模型"""
    phone: str
    captcha_id: str
    code: str


class CaptchaResponse(BaseSchema):
    """验证码响应模型"""
    captcha_id: str
    img: str  # base64编码的图片
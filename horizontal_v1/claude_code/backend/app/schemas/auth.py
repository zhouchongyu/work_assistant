"""
Authentication schemas (DTOs).

Reference:
- cool-admin-midway/src/modules/base/dto/login.ts
- Wiki: API参考文档/API参考文档.md
"""

from pydantic import Field

from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """Login request DTO."""

    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, max_length=100, description="Password")
    captcha_id: str = Field(..., alias="captchaId", description="Captcha ID")
    verify_code: str = Field(..., alias="verifyCode", description="Captcha verification code")


class LoginResponse(BaseSchema):
    """Login response DTO."""

    token: str = Field(..., description="Access token")
    expire: int = Field(..., description="Token expiration in seconds")
    refresh_token: str = Field(..., alias="refreshToken", description="Refresh token")
    refresh_expire: int = Field(..., alias="refreshExpire", description="Refresh token expiration in seconds")


class RefreshTokenRequest(BaseSchema):
    """Refresh token request DTO."""

    refresh_token: str = Field(..., alias="refreshToken", description="Refresh token")


class CaptchaResponse(BaseSchema):
    """Captcha response DTO."""

    captcha_id: str = Field(..., alias="captchaId", description="Captcha ID")
    data: str = Field(..., description="Captcha image data (base64 or SVG)")


class TokenPayload(BaseSchema):
    """JWT token payload."""

    user_id: int = Field(..., alias="userId", description="User ID")
    username: str = Field(..., description="Username")
    role_ids: list[int] = Field(default_factory=list, alias="roleIds", description="Role IDs")
    department_id: int | None = Field(None, alias="departmentId", description="Department ID")
    child_department_ids: list[int] = Field(
        default_factory=list, alias="childDepartmentIds", description="Child department IDs"
    )
    password_version: int = Field(1, alias="passwordVersion", description="Password version")
    nick_name: str | None = Field(None, alias="nickName", description="Nickname")
    is_refresh: bool = Field(False, alias="isRefresh", description="Is refresh token")
    dynamic_info: list[str] = Field(
        default_factory=list, alias="dynamicInfo", description="Dynamic column permissions"
    )


class UserInfoResponse(BaseSchema):
    """User info response DTO."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    name: str | None = Field(None, description="Real name")
    nick_name: str | None = Field(None, alias="nickName", description="Nickname")
    head_img: str | None = Field(None, alias="headImg", description="Avatar URL")
    email: str | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Phone")
    department_id: int | None = Field(None, alias="departmentId", description="Department ID")
    department_name: str | None = Field(None, alias="departmentName", description="Department name")
    role_ids: list[int] = Field(default_factory=list, alias="roleIds", description="Role IDs")
    status: int = Field(1, description="Status: 0=Disabled, 1=Enabled")


class PermsResponse(BaseSchema):
    """User permissions response DTO."""

    menus: list[dict] = Field(default_factory=list, description="Menu tree")
    perms: list[str] = Field(default_factory=list, description="Permission codes")


class ChangePasswordRequest(BaseSchema):
    """Change password request DTO."""

    old_password: str = Field(..., alias="oldPassword", description="Old password")
    new_password: str = Field(
        ..., alias="newPassword", min_length=6, max_length=50, description="New password"
    )


class UpdateUserInfoRequest(BaseSchema):
    """Update user info request DTO."""

    nick_name: str | None = Field(None, alias="nickName", description="Nickname")
    head_img: str | None = Field(None, alias="headImg", description="Avatar URL")
    email: str | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Phone")

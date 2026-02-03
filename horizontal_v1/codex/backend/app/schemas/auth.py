from __future__ import annotations

from backend.app.schemas.base import Schema


class CaptchaResponse(Schema):
    captcha_id: str
    data: str


class LoginRequest(Schema):
    username: str
    password: str
    captcha_id: str
    verify_code: str


class TokenPair(Schema):
    token: str
    expire: int
    refresh_token: str
    refresh_expire: int


class RefreshTokenRequest(Schema):
    refresh_token: str


class MeResponse(Schema):
    id: int
    username: str
    name: str | None = None
    nick_name: str | None = None
    department_id: int | None = None
    role_id_list: list[int] = []


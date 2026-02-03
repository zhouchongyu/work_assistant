from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.hash import pbkdf2_sha256

from backend.app.core.settings import Settings


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pbkdf2_sha256.verify(password, password_hash)
    except Exception:
        return False


def encode_token(payload: dict[str, Any], *, settings: Settings, expires_in_seconds: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=expires_in_seconds)
    token_payload = {**payload, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str, *, settings: Settings) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.core.config.settings import settings
from app.schemas.auth import LoginRequest, RefreshTokenRequest
from app.db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


class AuthService:
    """认证服务类"""

    @staticmethod
    async def authenticate_user(phone: str, password: str) -> Optional[dict]:
        """验证用户凭据"""
        from app.db.dao.user_dao import UserDao
        async for db in get_db_session():
            user = await UserDao.get_by_phone(db, phone)
            if not user:
                # 为了安全，即使用户不存在也返回False
                return None

            if not verify_password(password, user.hashed_password):
                return None

            # 返回用户信息
            return {
                "id": user.id,
                "phone": user.phone,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active
            }

    @staticmethod
    async def get_user_by_token(token: str) -> Optional[dict]:
        """根据令牌获取用户信息"""
        from app.db.dao.user_dao import UserDao
        payload = verify_token(token)
        if payload is None:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        async for db in get_db_session():
            user = await UserDao.get_by_id(db, user_id)
            if not user or not user.is_active:
                return None

            return {
                "id": user.id,
                "phone": user.phone,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
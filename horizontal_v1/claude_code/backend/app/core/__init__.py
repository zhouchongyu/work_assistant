"""Core infrastructure module."""

from app.core.config import get_settings, settings
from app.core.database import AsyncSessionLocal, Base, async_context_get_db, get_async_session
from app.core.deps import (
    AsyncSessionDep,
    CurrentUser,
    CurrentUserDep,
    PaginationDep,
    RedisDep,
    RequestIdDep,
)
from app.core.pagination import PageParams, PageResult, paginate, paginate_with_model
from app.core.redis import (
    CacheManager,
    CounterManager,
    DistributedLock,
    IdempotencyManager,
    get_redis,
    redis_client,
)
from app.core.repository import BaseRepository
from app.core.response import (
    ApiResponse,
    BusinessErrorResponse,
    ResponseCode,
    SuccessResponse,
    fail,
    success,
)

__all__ = [
    # Config
    "settings",
    "get_settings",
    # Database
    "Base",
    "AsyncSessionLocal",
    "get_async_session",
    "async_context_get_db",
    # Redis
    "redis_client",
    "get_redis",
    "DistributedLock",
    "IdempotencyManager",
    "CacheManager",
    "CounterManager",
    # Repository
    "BaseRepository",
    # Pagination
    "PageParams",
    "PageResult",
    "paginate",
    "paginate_with_model",
    # Response
    "ResponseCode",
    "ApiResponse",
    "SuccessResponse",
    "BusinessErrorResponse",
    "success",
    "fail",
    # Dependencies
    "AsyncSessionDep",
    "RedisDep",
    "PaginationDep",
    "RequestIdDep",
    "CurrentUser",
    "CurrentUserDep",
]

"""
FastAPI dependency injection helpers.

Provides common dependencies for routes and services.

Reference:
- assistant_py/db/async_deps.py: Original dependency injection
- Wiki: 后端服务/Python后端服务/Python后端服务.md
"""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends, Query, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PageParams
from app.core.redis import get_redis


# Type aliases for dependency injection
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    order: str | None = Query(None, description="Field to order by"),
    sort: str = Query("desc", description="Sort direction (asc/desc)"),
) -> PageParams:
    """
    FastAPI dependency for pagination parameters.

    Usage:
        @app.get("/items")
        async def get_items(
            params: PageParams = Depends(get_pagination_params),
            db: AsyncSession = Depends(get_async_session),
        ):
            ...
    """
    return PageParams(page=page, size=size, order=order, sort=sort)


PaginationDep = Annotated[PageParams, Depends(get_pagination_params)]


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.

    Usage:
        @app.get("/items")
        async def get_items(request_id: str = Depends(get_request_id)):
            ...
    """
    return getattr(request.state, "request_id", "unknown")


RequestIdDep = Annotated[str, Depends(get_request_id)]


class CurrentUser:
    """
    Placeholder for current user dependency.

    Will be implemented in Phase 3 (Auth module).
    """

    id: int
    username: str
    role_ids: list[int]
    department_id: int | None
    is_admin: bool

    def __init__(
        self,
        id: int = 0,
        username: str = "anonymous",
        role_ids: list[int] | None = None,
        department_id: int | None = None,
        is_admin: bool = False,
    ) -> None:
        self.id = id
        self.username = username
        self.role_ids = role_ids or []
        self.department_id = department_id
        self.is_admin = is_admin


async def get_current_user(request: Request) -> CurrentUser:
    """
    Get current authenticated user.

    This is a placeholder that will be replaced with actual
    JWT token validation in Phase 3.

    Usage:
        @app.get("/me")
        async def get_me(user: CurrentUser = Depends(get_current_user)):
            return {"id": user.id, "username": user.username}
    """
    # TODO: Implement actual JWT validation in Phase 3
    # For now, return anonymous user
    return CurrentUser()


async def get_current_user_optional(request: Request) -> CurrentUser | None:
    """
    Get current user if authenticated, None otherwise.

    Used for endpoints that work both authenticated and anonymously.
    """
    # TODO: Implement actual JWT validation in Phase 3
    return None


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserOptionalDep = Annotated[CurrentUser | None, Depends(get_current_user_optional)]


def require_permissions(*perms: str):
    """
    Decorator factory for requiring specific permissions.

    Will be implemented in Phase 3 (Auth module).

    Usage:
        @app.post("/users")
        @require_permissions("base:user:add")
        async def create_user(...):
            ...
    """
    def decorator(func: Any) -> Any:
        # TODO: Implement actual permission checking in Phase 3
        return func
    return decorator

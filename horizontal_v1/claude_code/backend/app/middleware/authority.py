"""
Authority middleware for permission checking.

Handles JWT token validation and permission checking for all API requests.

Reference:
- cool-admin-midway/src/modules/base/middleware/authority.ts
- Wiki: 后端服务/Python后端服务/后端架构补充/中间件系统/权限中间件.md
"""

import logging
import re
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.redis import CacheManager
from app.core.response import ApiResponse, ResponseCode
from app.services.auth import auth_service

logger = logging.getLogger("work_assistant.authority")


class AuthorityMiddleware(BaseHTTPMiddleware):
    """
    Authority middleware for JWT validation and permission checking.

    Flow:
    1. Extract token from Authorization header
    2. Verify JWT token
    3. Check password version (for forced logout on password change)
    4. Check user permissions against requested URL

    Special cases:
    - Skip auth for public endpoints (open, captcha, etc.)
    - Admin user bypasses permission checks
    - /comm/ endpoints are accessible by any logged-in user
    """

    # URLs that don't require authentication
    IGNORE_AUTH_PATTERNS = [
        r"^/api/v1/open/.*",           # Open endpoints (login, captcha)
        r"^/api/v1/app/.*",            # App public endpoints
        r"^/api/v1/dict/info/data$",   # Dictionary data (public access)
        r"^/health$",                   # Health check
        r"^/docs.*",                    # Swagger docs
        r"^/redoc.*",                   # ReDoc
        r"^/openapi\.json$",            # OpenAPI spec
        r"^/$",                         # Root endpoint
    ]

    # URLs that require login but not specific permissions
    COMM_PATTERNS = [
        r"^/api/v1/.*/comm/.*",        # Common endpoints
    ]

    def __init__(self, app: Callable, ignore_patterns: list[str] | None = None) -> None:
        super().__init__(app)
        self.ignore_patterns = [re.compile(p) for p in self.IGNORE_AUTH_PATTERNS]
        self.comm_patterns = [re.compile(p) for p in self.COMM_PATTERNS]
        if ignore_patterns:
            self.ignore_patterns.extend([re.compile(p) for p in ignore_patterns])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through authority middleware."""
        path = request.url.path
        method = request.method

        # Skip OPTIONS requests (CORS preflight)
        if method == "OPTIONS":
            return await call_next(request)

        # Check if URL should skip authentication
        if self._should_skip_auth(path):
            return await call_next(request)

        # Get token from Authorization header
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return self._unauthorized_response("请先登录")

        # Verify token
        try:
            payload = await auth_service.verify_token(token)
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return self._unauthorized_response("登录失效")

        # Store user info in request state
        request.state.user = payload
        request.state.user_id = payload.user_id
        request.state.username = payload.username
        request.state.role_ids = payload.role_ids
        request.state.department_id = payload.department_id
        request.state.is_admin = payload.username == "admin"

        # Verify cached token (SSO check)
        cached_token = await CacheManager.get(
            auth_service.CACHE_PREFIX_TOKEN, str(payload.user_id)
        )
        if cached_token and cached_token != token:
            # Token mismatch - user logged in elsewhere
            return self._unauthorized_response("登录失效")

        # Admin bypasses permission checks
        if payload.username == "admin":
            return await call_next(request)

        # Check if URL is a common endpoint (accessible by any logged-in user)
        if self._is_comm_url(path):
            return await call_next(request)

        # Check user permissions
        if not await self._check_permission(path, payload.user_id):
            return self._forbidden_response("无权限访问")

        return await call_next(request)

    def _should_skip_auth(self, path: str) -> bool:
        """Check if path should skip authentication."""
        for pattern in self.ignore_patterns:
            if pattern.match(path):
                return True
        return False

    def _is_comm_url(self, path: str) -> bool:
        """Check if path is a common endpoint."""
        for pattern in self.comm_patterns:
            if pattern.match(path):
                return True
        return False

    async def _check_permission(self, path: str, user_id: int) -> bool:
        """
        Check if user has permission for the requested URL.

        Permission matching:
        - URL: /api/v1/rk/supply/add
        - Permission: rk:supply:add

        Returns:
            True if permitted, False otherwise
        """
        # Get user permissions from cache
        perms = await CacheManager.get(auth_service.CACHE_PREFIX_PERMS, str(user_id))
        if not perms:
            return False

        # Convert URL to permission code
        # /api/v1/rk/supply/add -> rk/supply/add -> rk:supply:add
        perm_path = path.replace(settings.api_v1_prefix + "/", "").split("?")[0]

        # Convert cached permissions to URL format for comparison
        perm_urls = [p.replace(":", "/") for p in perms]

        return perm_path in perm_urls

    def _unauthorized_response(self, message: str) -> Response:
        """Create 401 Unauthorized response."""
        return ApiResponse(
            result=None,
            message=message,
            code=ResponseCode.UNAUTHORIZED,
            status_code=401,
        )

    def _forbidden_response(self, message: str) -> Response:
        """Create 403 Forbidden response."""
        return ApiResponse(
            result=None,
            message=message,
            code=ResponseCode.FORBIDDEN,
            status_code=403,
        )


def get_current_user_from_request(request: Request):
    """
    Extract current user from request state.

    Usage in route handlers:
        @app.get("/me")
        async def get_me(request: Request):
            user = get_current_user_from_request(request)
            return {"user_id": user.user_id}
    """
    from app.schemas.auth import TokenPayload

    user = getattr(request.state, "user", None)
    if user:
        return user
    return None

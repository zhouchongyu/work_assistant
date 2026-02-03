"""
Request ID middleware for request tracing.

This middleware:
1. Reads X-Request-ID from incoming request headers
2. Generates a new UUID if not present
3. Adds X-Request-ID to response headers
4. Makes request_id available to handlers via request.state

Reference:
- Wiki: 后端服务/Python后端服务/后端架构补充/中间件系统/中间件系统.md
- Wiki: 系统架构/系统架构.md (X-Request-ID requirement)
"""

import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for request ID (accessible across async calls)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_var.get()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle X-Request-ID header.

    - Reads existing X-Request-ID from request headers
    - Generates a new UUID if not present
    - Sets request_id in request.state for handler access
    - Adds X-Request-ID to response headers
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in context variable for async access
        token = request_id_var.set(request_id)

        # Store in request state for handler access
        request.state.request_id = request_id

        try:
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # Reset context variable
            request_id_var.reset(token)

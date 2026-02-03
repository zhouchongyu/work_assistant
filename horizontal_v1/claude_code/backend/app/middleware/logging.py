"""
Logging middleware for HTTP request/response logging.

This middleware logs:
- Request method, path, and timing
- Response status code
- Request ID for tracing

Reference:
- assistant_py/common/log.py: Original logging
- assistant_py/middleware/logging_interceptor.py: gRPC logging (for reference)
- Wiki: 后端服务/Python后端服务/后端架构补充/中间件系统/日志中间件.md
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.request_id import get_request_id

logger = logging.getLogger("work_assistant.http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured HTTP request/response logging.

    Logs include:
    - Request ID (X-Request-ID)
    - Method and path
    - Response status code
    - Request duration in milliseconds
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        start_time = time.time()
        request_id = get_request_id()

        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

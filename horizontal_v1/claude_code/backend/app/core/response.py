"""
Unified response format and JSON encoder.

Response code convention (aligned with cool-admin-vue frontend):
- 1000: Success
- 1001: Business failure (HTTP 200)
- Other codes: Specific error codes

Reference:
- assistant_py/common/responses/jsonResponse.py: Original response format
- cool-admin-vue/src/cool/service/request.ts: Frontend expected format
- Wiki: API参考文档/API参考文档.md
"""

import datetime
import decimal
import json
import time
from typing import Any

import orjson
from fastapi.responses import JSONResponse, ORJSONResponse


class ResponseCode:
    """Response code constants."""

    SUCCESS = 1000
    BUSINESS_ERROR = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    VALIDATION_ERROR = 1005
    INTERNAL_ERROR = 1006
    VERSION_CONFLICT = 1007


def json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for objects not serializable by default.

    Handles:
    - datetime/date/time objects
    - Decimal objects
    - bytes objects
    - SQLAlchemy model objects
    """
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    elif hasattr(obj, "__table__"):
        # SQLAlchemy model object
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def orjson_dumps(v: Any, *, default: Any = None) -> bytes:
    """
    Custom orjson dumps function with fallback serializer.
    """
    return orjson.dumps(v, default=default or json_serializer)


class ApiResponse(JSONResponse):
    """
    Unified API response class.

    Response format:
    {
        "code": 1000,           # 1000 for success, 1001+ for errors
        "message": "success",   # Human-readable message
        "result": {...},        # Response data
        "timestamp": 1234567890 # Unix timestamp in milliseconds
    }
    """

    media_type = "application/json"

    def __init__(
        self,
        result: Any = None,
        message: str = "success",
        code: int = ResponseCode.SUCCESS,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        content = {
            "code": code,
            "message": message,
            "result": result,
            "timestamp": int(time.time() * 1000),
        }
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            **kwargs,
        )

    def render(self, content: Any) -> bytes:
        """Render content as JSON bytes."""
        return orjson_dumps(content)


class SuccessResponse(ApiResponse):
    """Response for successful operations."""

    def __init__(
        self,
        result: Any = None,
        message: str = "success",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=result,
            message=message,
            code=ResponseCode.SUCCESS,
            status_code=200,
            **kwargs,
        )


class BusinessErrorResponse(ApiResponse):
    """
    Response for business logic errors.

    HTTP Status: 200 (to distinguish from system errors)
    Code: 1001
    """

    def __init__(
        self,
        message: str = "Business error",
        result: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=result,
            message=message,
            code=ResponseCode.BUSINESS_ERROR,
            status_code=200,
            **kwargs,
        )


class UnauthorizedResponse(ApiResponse):
    """Response for unauthorized access."""

    def __init__(
        self,
        message: str = "Unauthorized",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=None,
            message=message,
            code=ResponseCode.UNAUTHORIZED,
            status_code=401,
            **kwargs,
        )


class ForbiddenResponse(ApiResponse):
    """Response for forbidden access."""

    def __init__(
        self,
        message: str = "Forbidden",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=None,
            message=message,
            code=ResponseCode.FORBIDDEN,
            status_code=403,
            **kwargs,
        )


class NotFoundResponse(ApiResponse):
    """Response for resource not found."""

    def __init__(
        self,
        message: str = "Not found",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=None,
            message=message,
            code=ResponseCode.NOT_FOUND,
            status_code=404,
            **kwargs,
        )


class ValidationErrorResponse(ApiResponse):
    """Response for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result={"errors": errors or []},
            message=message,
            code=ResponseCode.VALIDATION_ERROR,
            status_code=422,
            **kwargs,
        )


class InternalErrorResponse(ApiResponse):
    """Response for internal server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            result=None,
            message=message,
            code=ResponseCode.INTERNAL_ERROR,
            status_code=500,
            **kwargs,
        )


def success(result: Any = None, message: str = "success") -> SuccessResponse:
    """Shortcut for creating a success response."""
    return SuccessResponse(result=result, message=message)


def fail(message: str = "Business error", result: Any = None) -> BusinessErrorResponse:
    """Shortcut for creating a business error response."""
    return BusinessErrorResponse(message=message, result=result)

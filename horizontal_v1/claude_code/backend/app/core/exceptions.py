"""
Custom exceptions and exception handlers.

Reference:
- assistant_py/common/exceptions/error.py: Original exceptions
- assistant_py/common/exceptions/__init__.py: Exception handlers
- Wiki: 后端服务/Python后端服务/Python后端服务.md
"""

from enum import Enum
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import (
    ApiResponse,
    BusinessErrorResponse,
    ForbiddenResponse,
    InternalErrorResponse,
    NotFoundResponse,
    ResponseCode,
    UnauthorizedResponse,
    ValidationErrorResponse,
)


class ErrorCode(Enum):
    """Error code enumeration."""

    SUCCESS = ("0000", "OK")
    FAILED = ("5000", "FAIL")
    FILE_NOT_EXIST = ("5005", "File not found")
    INVALID_TOKEN = ("1001", "Invalid token")
    EXPIRED_TOKEN = ("1002", "Token expired")
    PERMISSION_DENIED = ("1003", "Permission denied")
    RESOURCE_NOT_FOUND = ("1004", "Resource not found")
    VERSION_CONFLICT = ("1005", "Version conflict")
    VALIDATION_ERROR = ("1006", "Validation error")


class BusinessException(Exception):
    """
    Business logic exception.

    This exception returns HTTP 200 with code 1001 to indicate
    a business-level failure (not a system error).
    """

    def __init__(
        self,
        message: str = "Business error",
        code: str = "1001",
        result: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.result = result
        super().__init__(message)


class UnauthorizedException(Exception):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized") -> None:
        self.message = message
        super().__init__(message)


class ForbiddenException(Exception):
    """Forbidden access exception."""

    def __init__(self, message: str = "Forbidden") -> None:
        self.message = message
        super().__init__(message)


class NotFoundException(Exception):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)


class VersionConflictException(Exception):
    """Version conflict exception for optimistic locking."""

    def __init__(self, message: str = "Version conflict") -> None:
        self.message = message
        super().__init__(message)


class ValidationException(Exception):
    """Validation error exception."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message
        self.errors = errors or []
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application."""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(
        request: Request, exc: BusinessException
    ) -> ApiResponse:
        """Handle business logic exceptions."""
        return BusinessErrorResponse(message=exc.message, result=exc.result)

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(
        request: Request, exc: UnauthorizedException
    ) -> ApiResponse:
        """Handle unauthorized exceptions."""
        return UnauthorizedResponse(message=exc.message)

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(
        request: Request, exc: ForbiddenException
    ) -> ApiResponse:
        """Handle forbidden exceptions."""
        return ForbiddenResponse(message=exc.message)

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(
        request: Request, exc: NotFoundException
    ) -> ApiResponse:
        """Handle not found exceptions."""
        return NotFoundResponse(message=exc.message)

    @app.exception_handler(VersionConflictException)
    async def version_conflict_exception_handler(
        request: Request, exc: VersionConflictException
    ) -> ApiResponse:
        """Handle version conflict exceptions."""
        return ApiResponse(
            result=None,
            message=exc.message,
            code=ResponseCode.VERSION_CONFLICT,
            status_code=409,
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request, exc: ValidationException
    ) -> ApiResponse:
        """Handle validation exceptions."""
        return ValidationErrorResponse(message=exc.message, errors=exc.errors)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> ApiResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            })
        return ValidationErrorResponse(
            message="Request validation error",
            errors=errors,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> ApiResponse:
        """Handle Starlette HTTP exceptions."""
        status_code = exc.status_code
        detail = exc.detail or "An error occurred"

        if status_code == 401:
            return UnauthorizedResponse(message=str(detail))
        elif status_code == 403:
            return ForbiddenResponse(message=str(detail))
        elif status_code == 404:
            return NotFoundResponse(message=str(detail))
        elif status_code == 405:
            return ApiResponse(
                result=None,
                message="Method not allowed",
                code=1005,
                status_code=405,
            )
        else:
            return ApiResponse(
                result=None,
                message=str(detail),
                code=status_code,
                status_code=status_code,
            )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> ApiResponse:
        """Handle all unhandled exceptions."""
        # Log the exception for debugging
        import traceback
        traceback.print_exc()

        return InternalErrorResponse(
            message="Internal server error",
        )

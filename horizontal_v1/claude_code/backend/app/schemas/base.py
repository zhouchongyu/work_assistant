"""
Base Pydantic schemas and utilities.

Provides common patterns and utilities for API request/response schemas.

Key features:
- camelCase output (JSON serialization uses camelCase)
- Accept both snake_case and camelCase input
- Common field patterns

Reference:
- Wiki: API参考文档/API参考文档.md
- cool-admin-vue/src/cool/service/request.ts: Frontend expected format
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    """
    Convert snake_case to camelCase.

    Examples:
        to_camel("user_name") -> "userName"
        to_camel("created_at") -> "createdAt"
    """
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


class BaseSchema(BaseModel):
    """
    Base schema with camelCase aliasing.

    All schemas should inherit from this to ensure consistent
    API response format (camelCase for JSON output).
    """

    model_config = ConfigDict(
        # Use camelCase for JSON serialization
        alias_generator=to_camel,
        # Allow population by field name or alias
        populate_by_name=True,
        # Convert datetime to ISO format string
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None,
        },
        # Allow extra fields to be ignored
        extra="ignore",
        # Use enum values in serialization
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    """Schema mixin for timestamp fields."""

    create_time: datetime | None = Field(None, alias="createTime")
    update_time: datetime | None = Field(None, alias="updateTime")


class BusinessSchema(TimestampSchema):
    """Schema mixin for business entity fields."""

    created_by: int | None = Field(None, alias="createdBy")
    updated_by: int | None = Field(None, alias="updatedBy")
    department_id: int | None = Field(None, alias="departmentId")
    owner_id: int | None = Field(None, alias="ownerId")
    active: bool = True
    to_be_confirmed: bool = Field(False, alias="toBeConfirmed")
    reason: str | None = None


# Generic type for paginated results
T = TypeVar("T")


class PaginationParams(BaseSchema):
    """Pagination query parameters."""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    order: str | None = Field(None, description="Sort field")
    sort: str | None = Field("desc", description="Sort direction (asc/desc)")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper."""

    list: list[T] = Field(default_factory=list, description="List of items")
    pagination: dict[str, Any] = Field(
        default_factory=lambda: {"page": 1, "size": 20, "total": 0},
        description="Pagination info",
    )

    @classmethod
    def create(
        cls,
        items: list[T],
        page: int,
        size: int,
        total: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        return cls(
            list=items,
            pagination={
                "page": page,
                "size": size,
                "total": total,
            },
        )


class IdSchema(BaseSchema):
    """Schema for ID-based operations."""

    id: int = Field(..., description="Record ID")


class IdsSchema(BaseSchema):
    """Schema for batch ID operations."""

    ids: list[int] = Field(..., description="List of record IDs")


class MessageSchema(BaseSchema):
    """Simple message response schema."""

    message: str = Field(..., description="Response message")

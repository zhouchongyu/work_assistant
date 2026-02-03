"""
Dictionary schemas for API request/response.

Reference:
- cool-admin-midway/src/modules/dict/entity/type.ts
- cool-admin-midway/src/modules/dict/entity/info.ts
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ==================== DictType Schemas ====================


class DictTypeBase(BaseModel):
    """Base schema for dictionary type."""

    name: str = Field(..., description="Dictionary type name")
    key: str = Field(..., description="Dictionary type key (unique)")
    page: int = Field(default=0, description="Page number for grouping")


class DictTypeCreate(DictTypeBase):
    """Schema for creating dictionary type."""

    pass


class DictTypeUpdate(BaseModel):
    """Schema for updating dictionary type."""

    name: str | None = Field(default=None, description="Dictionary type name")
    key: str | None = Field(default=None, description="Dictionary type key")
    page: int | None = Field(default=None, description="Page number for grouping")


class DictTypeResponse(DictTypeBase):
    """Schema for dictionary type response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    createTime: datetime | None = Field(default=None, alias="createTime")
    updateTime: datetime | None = Field(default=None, alias="updateTime")


# ==================== DictInfo Schemas ====================


class DictInfoBase(BaseModel):
    """Base schema for dictionary info."""

    typeId: int = Field(..., description="Dictionary type ID")
    name: str = Field(..., description="Dictionary item name")
    value: str | None = Field(default=None, description="Dictionary item value")
    orderNum: int = Field(default=0, description="Sort order number")
    remark: str | None = Field(default=None, description="Remark or description")
    parentId: int | None = Field(default=None, description="Parent item ID")
    fieldName: str | None = Field(default=None, description="Associated field name")
    isShow: bool = Field(default=True, description="Whether to show in UI")
    isProcess: bool = Field(default=False, description="Whether to process as workflow")


class DictInfoCreate(DictInfoBase):
    """Schema for creating dictionary info."""

    pass


class DictInfoUpdate(BaseModel):
    """Schema for updating dictionary info."""

    typeId: int | None = Field(default=None, description="Dictionary type ID")
    name: str | None = Field(default=None, description="Dictionary item name")
    value: str | None = Field(default=None, description="Dictionary item value")
    orderNum: int | None = Field(default=None, description="Sort order number")
    remark: str | None = Field(default=None, description="Remark or description")
    parentId: int | None = Field(default=None, description="Parent item ID")
    fieldName: str | None = Field(default=None, description="Associated field name")
    isShow: bool | None = Field(default=None, description="Whether to show in UI")
    isProcess: bool | None = Field(default=None, description="Whether to process as workflow")


class DictInfoResponse(DictInfoBase):
    """Schema for dictionary info response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    createTime: datetime | None = Field(default=None, alias="createTime")
    updateTime: datetime | None = Field(default=None, alias="updateTime")


# ==================== Dict Data Schemas ====================


class DictDataRequest(BaseModel):
    """Schema for requesting dictionary data."""

    types: list[str] | None = Field(
        default=None, description="List of type keys to filter"
    )


class DictDataItem(BaseModel):
    """Schema for a single dictionary data item."""

    id: int
    name: str
    typeId: int
    parentId: int | None = None
    orderNum: int
    value: str | int | None
    label: str
    key: str


class DictDataResponse(BaseModel):
    """Schema for dictionary data response."""

    # Dynamic keys like "status_0", "type_0", etc.
    # Using dict[str, list[DictDataItem]] for the actual data
    pass


class DictGetValuesRequest(BaseModel):
    """Schema for getting dictionary values."""

    key: str = Field(..., description="Dictionary type key")
    value: str | list[str] = Field(..., description="Value or list of values to look up")


# ==================== Pagination Schemas ====================


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class DictTypeListParams(PaginationParams):
    """Parameters for listing dictionary types."""

    pass


class DictInfoListParams(PaginationParams):
    """Parameters for listing dictionary info."""

    typeId: int | None = Field(default=None, description="Filter by type ID")

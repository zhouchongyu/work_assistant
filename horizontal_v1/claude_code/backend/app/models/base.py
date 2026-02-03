"""
Base model mixins and utilities.

Provides common fields and patterns for all SQLAlchemy models.

Reference:
- assistant_py/app/v1/entity/base.py: Original base classes
- Wiki: 数据管理/实体模型/系统管理实体.md
- Wiki: 后端服务/Python后端服务/实体模型设计/实体模型设计.md
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """
    Mixin for automatic timestamp fields.

    Provides:
    - createTime: Set on record creation
    - updateTime: Updated on every modification
    """

    createTime: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="Record creation time",
    )
    updateTime: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="Record last update time",
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.

    Provides:
    - deletedAt: Timestamp when record was soft deleted (null if not deleted)
    """

    deletedAt: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=None,
        nullable=True,
        comment="Soft delete timestamp",
    )


class BusinessBase(TimestampMixin):
    """
    Base mixin for business entities.

    Provides common business fields:
    - createdBy: User who created the record
    - updatedBy: User who last updated the record
    - departmentId: Department association
    - ownerId: Owner user ID
    - active: Whether the record is active
    - toBeConfirmed: Pending confirmation flag
    - reason: Reason text for status changes
    """

    createdBy: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="User ID who created this record",
    )
    updatedBy: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="User ID who last updated this record",
    )
    departmentId: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Department ID",
    )
    ownerId: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Owner user ID",
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether the record is active",
    )
    toBeConfirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Pending confirmation flag",
    )
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason text for status changes",
    )


class VersionMixin:
    """
    Mixin for optimistic locking with version control.

    Provides:
    - version: Auto-incrementing version number for optimistic locking
    """

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Version number for optimistic locking",
    )


def to_dict(
    obj: Any,
    exclude: set[str] | None = None,
    include: set[str] | None = None,
) -> dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a dictionary.

    Args:
        obj: SQLAlchemy model instance
        exclude: Set of column names to exclude
        include: Set of column names to include (if provided, only these are included)

    Returns:
        Dictionary representation of the model
    """
    if not hasattr(obj, "__table__"):
        raise ValueError("Object must be a SQLAlchemy model instance")

    exclude = exclude or set()
    result = {}

    for column in obj.__table__.columns:
        if include and column.name not in include:
            continue
        if column.name in exclude:
            continue
        result[column.name] = getattr(obj, column.name)

    return result

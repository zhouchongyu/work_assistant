"""
Dictionary entities.

Provides dictionary type and info storage for system configuration.

Reference:
- cool-admin-midway/src/modules/dict/entity/type.ts
- cool-admin-midway/src/modules/dict/entity/info.ts
- Wiki: 前端系统/业务模块/其他业务模块/字典模块.md
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class DictType(Base, TimestampMixin):
    """
    Dictionary type entity.

    Groups dictionary items by type for organized management.
    """

    __tablename__ = "dict_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Dictionary type name"
    )
    key: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, comment="Dictionary type key"
    )
    page: Mapped[int] = mapped_column(
        Integer, default=0, comment="Page number for grouping"
    )

    # Relationships
    items: Mapped[list["DictInfo"]] = relationship(
        "DictInfo", back_populates="dict_type", cascade="all, delete-orphan"
    )


class DictInfo(Base, TimestampMixin):
    """
    Dictionary info entity.

    Stores individual dictionary items with values and ordering.
    """

    __tablename__ = "dict_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    typeId: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dict_type.id", ondelete="CASCADE"),
        nullable=False,
        comment="Dictionary type ID",
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Dictionary item name"
    )
    value: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Dictionary item value"
    )
    orderNum: Mapped[int] = mapped_column(
        Integer, default=0, comment="Sort order number"
    )
    remark: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Remark or description"
    )
    parentId: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Parent item ID for tree structure"
    )
    fieldName: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Associated field name"
    )
    isShow: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Whether to show in UI"
    )
    isProcess: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Whether to process as workflow"
    )

    # Relationships
    dict_type: Mapped["DictType"] = relationship("DictType", back_populates="items")

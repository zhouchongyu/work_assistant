from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class SysRole(Base, TimestampMixin):
    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    label: Mapped[str | None] = mapped_column(sa.String(50), unique=True, nullable=True)
    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    relevance: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class SysDepartment(Base, TimestampMixin):
    __tablename__ = "sys_department"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(sa.String(255))
    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    order_num: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)


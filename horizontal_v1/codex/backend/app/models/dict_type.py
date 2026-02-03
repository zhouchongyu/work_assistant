from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class DictType(Base, TimestampMixin):
    __tablename__ = "dict_type"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(sa.String(255))
    key: Mapped[str] = mapped_column(sa.String(255), index=True)
    page: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)


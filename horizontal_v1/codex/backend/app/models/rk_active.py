from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class RkActive(Base, TimestampMixin):
    __tablename__ = "rk_active"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, unique=True, index=True)
    status: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)


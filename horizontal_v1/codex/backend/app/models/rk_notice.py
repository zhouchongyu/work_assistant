from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkNotice(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_notice"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    receiver_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    content: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False, index=True)

    model: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    from_user: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    type: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)


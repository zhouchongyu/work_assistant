from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkSharedLinks(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_shared_links"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    resource_type: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)
    resource_id: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)
    share_token: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, unique=True)

    expire_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False, index=True)


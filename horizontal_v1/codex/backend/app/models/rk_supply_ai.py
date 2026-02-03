from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class RkSupplyAi(Base, TimestampMixin):
    __tablename__ = "rk_supply_ai"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    supply_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)

    work_experience: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    basic: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    x_raw: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    y_raw: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    z_raw: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    x_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    y_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    z_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)


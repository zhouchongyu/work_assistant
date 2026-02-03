from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkMatchRes(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_match_res"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    demand_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    supply_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)

    score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    warning_msg: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    demand_role: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    years_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    demand_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    supply_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    type: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)
    msg: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)

    reject_type: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)


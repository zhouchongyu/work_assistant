from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkSupplyDemandLink(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_supply_demand_link"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    supply_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    demand_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    status: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)
    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    result: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    k: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    supply_demand_status1: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_demand_status2: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_demand_status3: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)
    supply_demand_status4: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_demand_status5: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    tag: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    tag_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    demand_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    years: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    father_skill: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    demand_role: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    demand_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    supply_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    warning_msg: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)


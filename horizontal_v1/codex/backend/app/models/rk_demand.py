from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkDemand(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_demand"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)
    name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    customer_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    customer_contact_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    price: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    work_location: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    skillx: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    skilly: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    skillz: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    japanese_level: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    english_level: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    role: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    father_skill: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    change_status: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    unit_price_max: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    work_percent: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    citizenship: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    role_list: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)
    version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    have_match: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    analysis_status: Mapped[str | None] = mapped_column(sa.String(100), nullable=True, index=True)


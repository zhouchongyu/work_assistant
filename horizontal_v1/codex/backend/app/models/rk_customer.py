from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkCustomer(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_customer"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(100), index=True)

    director: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    check: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    check_remark: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    customer_status1: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status2: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status3: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status4: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status5: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status6: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status7: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status8: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status9: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    customer_status10: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    enterprise_id: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)


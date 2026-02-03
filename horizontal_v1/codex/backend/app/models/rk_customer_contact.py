from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkCustomerContact(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_customer_contact"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    postal: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    is_default: Mapped[bool | None] = mapped_column("default", sa.Boolean, nullable=True)

    name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    position: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    customer_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)


from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkCustomerColumn(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_customer_column"
    __table_args__ = (
        sa.UniqueConstraint("owner_id", "name", name="uq_rk_customer_column_owner_id_name"),
    )

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(sa.String(200), nullable=False, index=True)
    column_info: Mapped[str] = mapped_column(sa.Text, nullable=False)


from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkVendor(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_vendor"
    __table_args__ = (sa.UniqueConstraint("name", "owner_id", name="uq_rk_vendor_name_owner_id"),)

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

    vendor_status1: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status2: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status3: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status4: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status5: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status6: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status7: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status8: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status9: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    vendor_status10: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    enterprise_id: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    folder_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    folder_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    delta_link: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    folder_update: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)


from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class RkCaseStatus(Base, TimestampMixin):
    __tablename__ = "rk_case_status"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    case_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    status: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    remark: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False, index=True)


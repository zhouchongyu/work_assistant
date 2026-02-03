from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class RkLlmData(Base, TimestampMixin):
    __tablename__ = "rk_llm_data"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    demand_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    supply_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    event_type: Mapped[str | None] = mapped_column(sa.String(100), nullable=True, index=True)
    res: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    model: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    special: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    third_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    context: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    demand_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    supply_version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)


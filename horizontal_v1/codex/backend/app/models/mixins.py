from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )


class BusinessMixin:
    created_by: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    updated_by: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    department_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    owner_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False, index=True)
    to_be_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

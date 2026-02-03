from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class SysMenu(Base, TimestampMixin):
    __tablename__ = "sys_menu"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(255))

    router: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    perms: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    type: Mapped[int] = mapped_column(sa.SmallInteger, default=0, nullable=False)
    icon: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    order_num: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    view_path: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    keep_alive: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    is_show: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)

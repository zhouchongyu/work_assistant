from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class SysUser(Base, TimestampMixin):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    department_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)

    username: Mapped[str] = mapped_column(sa.String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255))
    password_version: Mapped[int] = mapped_column(sa.Integer, default=1, nullable=False)

    name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    nick_name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    head_img: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    status: Mapped[int] = mapped_column(sa.SmallInteger, default=1, nullable=False)
    socket_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

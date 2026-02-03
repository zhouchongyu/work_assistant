from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin


class DictInfo(Base, TimestampMixin):
    __tablename__ = "dict_info"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    type_id: Mapped[int] = mapped_column(sa.BigInteger, index=True)
    name: Mapped[str] = mapped_column(sa.String(255))
    value: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    order_num: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    field_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    is_show: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    is_process: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)


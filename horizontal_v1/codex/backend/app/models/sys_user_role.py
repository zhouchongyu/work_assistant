from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class SysUserRole(Base):
    __tablename__ = "sys_user_role"

    user_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)
    role_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)


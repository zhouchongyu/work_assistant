from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class SysRoleMenu(Base):
    __tablename__ = "sys_role_menu"

    role_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)
    menu_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)


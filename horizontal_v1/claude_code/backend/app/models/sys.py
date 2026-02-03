"""
System RBAC entities: User, Role, Menu, Department.

Reference:
- cool-admin-midway/src/modules/base/entity/sys/user.ts
- cool-admin-midway/src/modules/base/entity/sys/role.ts
- cool-admin-midway/src/modules/base/entity/sys/menu.ts
- cool-admin-midway/src/modules/base/entity/sys/department.ts
- Wiki: 数据管理/实体模型/系统管理实体.md
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    pass


class BaseSysDepartment(Base, TimestampMixin):
    """
    Department entity.

    Table: base_sys_department
    """

    __tablename__ = "base_sys_department"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Department name")
    parentId: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Parent department ID"
    )
    orderNum: Mapped[int] = mapped_column(Integer, default=0, comment="Sort order")

    # Relationships
    users: Mapped[list["BaseSysUser"]] = relationship(
        "BaseSysUser", back_populates="department", lazy="selectin"
    )


class BaseSysRole(Base, TimestampMixin):
    """
    Role entity.

    Table: base_sys_role
    """

    __tablename__ = "base_sys_role"
    __table_args__ = (
        Index("ix_base_sys_role_name", "name", unique=True),
        Index("ix_base_sys_role_label", "label", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Creator user ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Role name")
    label: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Role label")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")
    relevance: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Data permission relates to hierarchy"
    )
    menuIdList: Mapped[list[int] | None] = mapped_column(
        JSONB, nullable=True, comment="Menu permission IDs"
    )
    departmentIdList: Mapped[list[int] | None] = mapped_column(
        JSONB, nullable=True, comment="Department permission IDs"
    )

    # Relationships
    user_roles: Mapped[list["BaseSysUserRole"]] = relationship(
        "BaseSysUserRole", back_populates="role", lazy="selectin"
    )


class BaseSysMenu(Base, TimestampMixin):
    """
    Menu entity.

    Table: base_sys_menu
    Type: 0=Directory, 1=Menu, 2=Button
    """

    __tablename__ = "base_sys_menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parentId: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Parent menu ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Menu name")
    router: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Router path")
    perms: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Permission code")
    type: Mapped[int] = mapped_column(
        Integer, default=0, comment="Type: 0=Directory, 1=Menu, 2=Button"
    )
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Icon")
    orderNum: Mapped[int] = mapped_column(Integer, default=0, comment="Sort order")
    viewPath: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="View path")
    keepAlive: Mapped[bool] = mapped_column(Boolean, default=True, comment="Keep alive")
    isShow: Mapped[bool] = mapped_column(Boolean, default=True, comment="Is visible")


class BaseSysUser(Base, TimestampMixin):
    """
    User entity.

    Table: base_sys_user
    """

    __tablename__ = "base_sys_user"
    __table_args__ = (
        Index("ix_base_sys_user_username", "username", unique=True),
        Index("ix_base_sys_user_department_id", "departmentId"),
        Index("ix_base_sys_user_phone", "phone"),
        Index("ix_base_sys_user_email", "email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    departmentId: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("base_sys_department.id", ondelete="SET NULL"),
        nullable=True,
        comment="Department ID",
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Real name")
    username: Mapped[str] = mapped_column(String(100), nullable=False, comment="Username")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="Password hash")
    passwordV: Mapped[int] = mapped_column(
        Integer, default=1, comment="Password version (for token invalidation)"
    )
    nickName: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Nickname")
    headImg: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="Avatar URL")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="Phone number")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Email")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="Status: 0=Disabled, 1=Enabled"
    )
    socketId: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Socket ID")

    # Relationships
    department: Mapped["BaseSysDepartment | None"] = relationship(
        "BaseSysDepartment", back_populates="users", lazy="selectin"
    )
    user_roles: Mapped[list["BaseSysUserRole"]] = relationship(
        "BaseSysUserRole", back_populates="user", lazy="selectin"
    )


class BaseSysUserRole(Base, TimestampMixin):
    """
    User-Role association entity.

    Table: base_sys_user_role
    """

    __tablename__ = "base_sys_user_role"
    __table_args__ = (Index("ix_base_sys_user_role_user_id", "userId"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_sys_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    roleId: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_sys_role.id", ondelete="CASCADE"),
        nullable=False,
        comment="Role ID",
    )

    # Relationships
    user: Mapped["BaseSysUser"] = relationship("BaseSysUser", back_populates="user_roles")
    role: Mapped["BaseSysRole"] = relationship("BaseSysRole", back_populates="user_roles")


class BaseSysLog(Base, TimestampMixin):
    """
    Operation log entity.

    Table: base_sys_log
    """

    __tablename__ = "base_sys_log"
    __table_args__ = (Index("ix_base_sys_log_user_id", "userId"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="User ID")
    action: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Action")
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="IP address")
    ipAddr: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="IP location")
    params: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Request params")


class BaseSysParam(Base, TimestampMixin):
    """
    System parameter entity.

    Table: base_sys_param
    """

    __tablename__ = "base_sys_param"
    __table_args__ = (Index("ix_base_sys_param_key", "keyName", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyName: Mapped[str] = mapped_column(String(100), nullable=False, comment="Parameter key")
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Parameter name")
    data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Parameter value")
    dataType: Mapped[int] = mapped_column(
        Integer, default=0, comment="Data type: 0=String, 1=RichText, 2=File"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remark")


class BaseSysConf(Base, TimestampMixin):
    """
    System configuration entity.

    Table: base_sys_conf
    """

    __tablename__ = "base_sys_conf"
    __table_args__ = (Index("ix_base_sys_conf_key", "cKey", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cKey: Mapped[str] = mapped_column(String(100), nullable=False, comment="Config key")
    cValue: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Config value")

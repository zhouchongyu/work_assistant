from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class SysParam(Base, TimestampMixin):
    """系统参数表"""
    __tablename__ = "sys_param"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), unique=True, nullable=False, comment="参数键名")
    name = Column(String(100), nullable=False, comment="参数名称")
    value = Column(Text, comment="参数值")
    data_type = Column(String(20), default="string", comment="数据类型(string,number,boolean,json)")
    description = Column(String(500), comment="参数描述")


class Menu(Base, TimestampMixin):
    """菜单表"""
    __tablename__ = "sys_menu"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="菜单名称")
    parent_id = Column(Integer, ForeignKey("sys_menu.id"), comment="父级菜单ID")
    path = Column(String(200), nullable=False, comment="路由路径")
    component = Column(String(200), comment="组件路径")
    redirect = Column(String(200), comment="重定向路径")
    icon = Column(String(100), comment="菜单图标")
    sort = Column(Integer, default=0, comment="排序")
    hidden = Column(Boolean, default=False, comment="是否隐藏")
    description = Column(String(500), comment="菜单描述")

    # 自关联关系
    parent = relationship("Menu", remote_side=[id], backref="children")


class Department(Base, TimestampMixin):
    """部门表"""
    __tablename__ = "sys_department"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("sys_department.id"), comment="父级部门ID")
    leader_id = Column(Integer, comment="负责人ID")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    description = Column(String(500), comment="部门描述")

    # 自关联关系
    parent = relationship("Department", remote_side=[id], backref="children")


class Role(Base, TimestampMixin):
    """角色表"""
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="角色名称")
    code = Column(String(100), unique=True, nullable=False, comment="角色编码")
    description = Column(String(500), comment="角色描述")

    # 关系：角色与菜单
    menus = relationship("Menu", secondary="sys_role_menu", back_populates="roles")


class RoleMenu(Base):
    """角色菜单关联表"""
    __tablename__ = "sys_role_menu"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("sys_menu.id"), nullable=False)


class UserDepartment(Base):
    """用户部门关联表"""
    __tablename__ = "sys_user_department"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("sys_department.id"), nullable=False)


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "sys_user_role"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False)
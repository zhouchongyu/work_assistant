from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    avatar = Column(String(255))  # 头像URL
    department_id = Column(Integer)  # 部门ID
    position = Column(String(100))  # 职位
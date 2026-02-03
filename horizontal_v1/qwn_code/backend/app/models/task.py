from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin


class TaskInfo(Base, TimestampMixin):
    """任务信息表"""
    __tablename__ = "task_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="任务名称")
    type = Column(Integer, nullable=False, comment="任务类型")
    cron_expression = Column(String(100), nullable=False, comment="CRON表达式")
    handler = Column(String(500), nullable=False, comment="处理器")
    description = Column(Text, comment="任务描述")
    enabled = Column(Boolean, default=True, comment="是否启用")
    status = Column(String(50), default="STOPPED", comment="任务状态")
    last_run_time = Column(DateTime, comment="最后运行时间")
    next_run_time = Column(DateTime, comment="下次运行时间")


class TaskLog(Base, TimestampMixin):
    """任务日志表"""
    __tablename__ = "task_log"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task_info.id"), nullable=False, comment="任务ID")
    status = Column(String(50), nullable=False, comment="执行状态")
    message = Column(Text, comment="执行消息")

    # 关系
    task = relationship("TaskInfo", back_populates="logs")


# 添加反向关系
TaskInfo.logs = relationship("TaskLog", order_by=TaskLog.id, back_populates="task")
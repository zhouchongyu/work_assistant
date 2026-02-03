"""
Task scheduling models.

Reference:
- cool-admin-midway/src/modules/task/entity/info.ts
- cool-admin-midway/src/modules/task/entity/log.ts
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class TaskInfo(Base, TimestampMixin):
    """
    Task information entity.

    Represents a scheduled task configuration.
    """

    __tablename__ = "task_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Task name")
    cron: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Cron expression")
    every: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Interval in milliseconds (if cron is not set)"
    )
    limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Max execution count (null for unlimited)"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="Status: 0=stopped, 1=running"
    )
    taskType: Mapped[int] = mapped_column(
        Integer, default=0, comment="Task type: 0=cron, 1=interval"
    )
    type: Mapped[int] = mapped_column(
        Integer, default=0, comment="Type: 0=system, 1=user"
    )
    service: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Service method to invoke (e.g., 'SupplyService.analyze(123)')"
    )
    data: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Task data (JSON)"
    )
    remark: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Remarks"
    )
    startDate: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Start date for scheduling"
    )
    endDate: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="End date for scheduling"
    )
    nextRunTime: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Next scheduled run time"
    )
    jobId: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="APScheduler job ID"
    )
    repeatConf: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="Repeat configuration (JSON)"
    )


class TaskLog(Base, TimestampMixin):
    """
    Task execution log entity.

    Records task execution history.
    """

    __tablename__ = "task_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taskId: Mapped[int] = mapped_column(Integer, nullable=False, comment="Task ID", index=True)
    status: Mapped[int] = mapped_column(
        Integer, default=0, comment="Status: 0=failed, 1=success"
    )
    detail: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Execution detail/error message"
    )

    __table_args__ = (
        Index("idx_task_log_task_id", "taskId"),
    )

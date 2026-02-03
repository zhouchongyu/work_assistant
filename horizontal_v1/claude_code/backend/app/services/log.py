"""
Operation log service.

Records user operations for audit trail.

Reference:
- cool-admin-midway/src/modules/base/service/sys/log.ts
- cool-admin-midway/src/modules/base/middleware/log.ts
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.sys import BaseSysLog, BaseSysUser
from app.services.conf import conf_service

logger = logging.getLogger("work_assistant.log")


class LogRepository(BaseRepository[BaseSysLog]):
    """Repository for BaseSysLog entity."""

    model = BaseSysLog


class LogService:
    """
    Operation log service.

    Features:
    - Record user operations
    - Automatic IP extraction
    - Log retention management
    """

    def __init__(self) -> None:
        self.repo = LogRepository()

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Checks X-Forwarded-For header first, then falls back to client host.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get the first IP in the chain
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def record(
        self,
        db: AsyncSession,
        request: Request,
        user_id: int | None,
        params: dict | None = None,
    ) -> None:
        """
        Record an operation log entry.

        Args:
            db: Database session
            request: FastAPI request object
            user_id: User ID performing the action
            params: Request parameters (optional)
        """
        ip = self._get_client_ip(request)
        action = request.url.path.split("?")[0]

        log = BaseSysLog(
            userId=user_id,
            ip=ip,
            action=action,
            params=params,
        )

        db.add(log)
        await db.commit()
        logger.debug(f"Recorded log: user={user_id}, action={action}, ip={ip}")

    async def clear(self, db: AsyncSession, clear_all: bool = False) -> None:
        """
        Clear operation logs.

        Args:
            db: Database session
            clear_all: If True, clear all logs. Otherwise, keep logs based on retention setting.
        """
        if clear_all:
            stmt = delete(BaseSysLog)
            await db.execute(stmt)
            await db.commit()
            logger.info("Cleared all operation logs")
            return

        # Get retention period from config
        keep_days = await conf_service.get_value(db, "logKeep")
        if keep_days:
            try:
                days = int(keep_days)
                before_date = datetime.now() - timedelta(days=days)
                stmt = delete(BaseSysLog).where(
                    BaseSysLog.createTime < before_date
                )
                await db.execute(stmt)
                await db.commit()
                logger.info(f"Cleared logs older than {days} days")
            except ValueError:
                # Invalid config, clear all
                stmt = delete(BaseSysLog)
                await db.execute(stmt)
                await db.commit()
                logger.warning("Invalid logKeep config, cleared all logs")
        else:
            # No retention config, clear all
            stmt = delete(BaseSysLog)
            await db.execute(stmt)
            await db.commit()
            logger.info("No logKeep config, cleared all logs")

    async def set_keep_days(self, db: AsyncSession, days: int) -> None:
        """
        Set log retention period.

        Args:
            db: Database session
            days: Number of days to keep logs
        """
        await conf_service.update_value(db, "logKeep", str(days))

    async def get_keep_days(self, db: AsyncSession) -> int | None:
        """
        Get log retention period.

        Args:
            db: Database session

        Returns:
            Number of days to keep logs, or None if not set
        """
        value = await conf_service.get_value(db, "logKeep")
        if value:
            try:
                return int(value)
            except ValueError:
                return None
        return None

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        keyword: str | None = None,
    ) -> dict[str, Any]:
        """
        List operation logs with pagination.

        Joins with user table to get username.

        Args:
            db: Database session
            page: Page number
            size: Page size
            keyword: Search keyword (searches name, action, ip)

        Returns:
            Paginated log list with user info
        """
        # Build query with join
        offset = (page - 1) * size

        # Count total
        count_stmt = select(BaseSysLog)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Fetch logs with user info
        stmt = (
            select(
                BaseSysLog.id,
                BaseSysLog.userId,
                BaseSysLog.action,
                BaseSysLog.ip,
                BaseSysLog.ipAddr,
                BaseSysLog.params,
                BaseSysLog.createTime,
                BaseSysUser.name.label("userName"),
            )
            .outerjoin(BaseSysUser, BaseSysLog.userId == BaseSysUser.id)
            .order_by(BaseSysLog.createTime.desc())
            .offset(offset)
            .limit(size)
        )

        result = await db.execute(stmt)
        rows = result.all()

        logs = [
            {
                "id": row.id,
                "userId": row.userId,
                "action": row.action,
                "ip": row.ip,
                "ipAddr": row.ipAddr,
                "params": row.params,
                "createTime": row.createTime.isoformat() if row.createTime else None,
                "name": row.userName,
            }
            for row in rows
        ]

        return {
            "list": logs,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
            },
        }


# Singleton instance
log_service = LogService()

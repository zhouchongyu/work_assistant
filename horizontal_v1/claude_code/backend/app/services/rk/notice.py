"""
Notice service.

Handles notification management.

Reference:
- assistant_py/app/v1/dao/noticeDao.py
- assistant_py/common/send_notice.py
"""

import logging
from typing import Any

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.rk import RkNotice

logger = logging.getLogger("work_assistant.rk.notice")


class NoticeRepository(BaseRepository[RkNotice]):
    """Repository for RkNotice entity."""

    model = RkNotice


class NoticeService:
    """
    Notice service.

    Features:
    - Notice CRUD operations
    - Mark as read functionality
    - Unread count
    """

    def __init__(self) -> None:
        self.repo = NoticeRepository()

    # ==================== CRUD Operations ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkNotice | None:
        """Create a new notice."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, notice_id: int
    ) -> RkNotice | None:
        """Get notice by ID."""
        return await self.repo.get_by_id(notice_id, db)

    async def update(
        self, db: AsyncSession, notice_id: int, data: dict[str, Any]
    ) -> bool:
        """Update notice by ID."""
        return await self.repo.update_by_id(notice_id, data, db)

    async def delete(self, db: AsyncSession, notice_id: int) -> bool:
        """Delete notice by ID."""
        return await self.repo.delete_by_id(notice_id, db)

    # ==================== Read/Unread ====================

    async def mark_as_read(
        self, db: AsyncSession, notice_id: int
    ) -> bool:
        """Mark a notice as read."""
        return await self.update(db, notice_id, {"isRead": True})

    async def mark_all_as_read(
        self, db: AsyncSession, user_id: int
    ) -> None:
        """Mark all notices as read for a user."""
        stmt = (
            update(RkNotice)
            .where(
                and_(
                    RkNotice.recieverId == user_id,
                    RkNotice.isRead == False,
                )
            )
            .values(isRead=True)
        )
        await db.execute(stmt)
        await db.commit()

    async def get_unread_count(
        self, db: AsyncSession, user_id: int
    ) -> int:
        """Get unread notice count for a user."""
        stmt = select(RkNotice).where(
            and_(
                RkNotice.recieverId == user_id,
                RkNotice.isRead == False,
                RkNotice.active == True,
            )
        )
        result = await db.execute(stmt)
        return len(result.scalars().all())

    # ==================== List Operations ====================

    async def list_by_receiver(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        size: int = 20,
        unread_only: bool = False,
    ) -> dict[str, Any]:
        """List notices for a user."""
        conditions = {"recieverId": user_id, "active": True}
        if unread_only:
            conditions["isRead"] = False

        return await self.repo.find_with_pagination(
            db,
            conditions=conditions,
            page=page,
            size=size,
            order_by=[("createTime", "desc")],
        )

    async def list_by_type(
        self,
        db: AsyncSession,
        user_id: int,
        notice_type: str,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """List notices by type for a user."""
        return await self.repo.find_with_pagination(
            db,
            conditions={
                "recieverId": user_id,
                "type": notice_type,
                "active": True,
            },
            page=page,
            size=size,
            order_by=[("createTime", "desc")],
        )

    # ==================== Send Notice ====================

    async def send_notice(
        self,
        db: AsyncSession,
        receiver_id: int,
        content: str,
        notice_type: str = "",
        from_user: int | None = None,
        model: str | None = None,
        to_be_confirmed: bool = False,
        reason: str | None = None,
    ) -> RkNotice | None:
        """
        Send a notice to a user.

        Args:
            db: Database session
            receiver_id: Recipient user ID
            content: Notice content
            notice_type: Notice type
            from_user: Sender user ID
            model: Related model name
            to_be_confirmed: Whether confirmation is needed
            reason: Reason for notice

        Returns:
            Created notice
        """
        notice = await self.create(
            db,
            {
                "recieverId": receiver_id,
                "content": content,
                "type": notice_type,
                "fromUser": from_user,
                "model": model,
                "toBeConfirmed": to_be_confirmed,
                "reason": reason,
                "isRead": False,
                "active": True,
            },
        )

        if notice:
            # TODO: Send MQTT notification for real-time update
            logger.info(
                f"Notice sent to user {receiver_id}: {content[:50]}..."
            )

        return notice


# Singleton instance
notice_service = NoticeService()

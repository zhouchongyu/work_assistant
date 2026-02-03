"""
System configuration service.

Provides simple key-value configuration storage.

Reference:
- cool-admin-midway/src/modules/base/service/sys/conf.ts
"""

import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.sys import BaseSysConf

logger = logging.getLogger("work_assistant.conf")


class ConfRepository(BaseRepository[BaseSysConf]):
    """Repository for BaseSysConf entity."""

    model = BaseSysConf


class ConfService:
    """
    System configuration service.

    Simple key-value storage for system settings.
    """

    def __init__(self) -> None:
        self.repo = ConfRepository()

    async def get_value(self, db: AsyncSession, key: str) -> str | None:
        """
        Get configuration value by key.

        Args:
            db: Database session
            key: Configuration key

        Returns:
            Configuration value or None
        """
        stmt = select(BaseSysConf).where(BaseSysConf.cKey == key)
        result = await db.execute(stmt)
        conf = result.scalar_one_or_none()
        return conf.cValue if conf else None

    async def update_value(
        self, db: AsyncSession, key: str, value: str
    ) -> None:
        """
        Update configuration value by key.

        Creates the key if it doesn't exist.

        Args:
            db: Database session
            key: Configuration key
            value: Configuration value
        """
        # Check if key exists
        stmt = select(BaseSysConf).where(BaseSysConf.cKey == key)
        result = await db.execute(stmt)
        conf = result.scalar_one_or_none()

        if conf:
            # Update existing
            update_stmt = (
                update(BaseSysConf)
                .where(BaseSysConf.cKey == key)
                .values(cValue=value)
            )
            await db.execute(update_stmt)
        else:
            # Create new
            new_conf = BaseSysConf(cKey=key, cValue=value)
            db.add(new_conf)

        await db.commit()


# Singleton instance
conf_service = ConfService()

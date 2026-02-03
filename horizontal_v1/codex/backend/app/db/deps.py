from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_async_sessionmaker


async def get_db_session() -> AsyncIterator[AsyncSession]:
    sessionmaker = get_async_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


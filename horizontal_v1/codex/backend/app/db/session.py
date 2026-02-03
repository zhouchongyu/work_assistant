from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app.core.settings import Settings, get_settings
from backend.app.db.base import DEFAULT_SCHEMA


def create_async_engine_from_settings(settings: Settings) -> AsyncEngine:
    if settings.database_url.startswith("sqlite"):
        return create_async_engine(
            settings.database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            execution_options={
                "schema_translate_map": {DEFAULT_SCHEMA: None, "wa_v3_migration": None},
            },
        )
    return create_async_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_async_engine() -> AsyncEngine:
    return create_async_engine_from_settings(get_settings())


def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(get_async_engine(), expire_on_commit=False)

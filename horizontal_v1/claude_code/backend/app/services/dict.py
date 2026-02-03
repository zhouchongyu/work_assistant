"""
Dictionary service with Redis read-through cache.

Provides dictionary data management with caching for performance.

Reference:
- cool-admin-midway/src/modules/dict/service/info.ts
- Wiki: 后端服务/Python后端服务/后端架构补充/服务层架构/字典服务模块.md
"""

import hashlib
import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import CacheManager
from app.core.repository import BaseRepository
from app.models.dict import DictInfo, DictType

logger = logging.getLogger("work_assistant.dict")


class DictTypeRepository(BaseRepository[DictType]):
    """Repository for DictType entity."""

    model = DictType


class DictInfoRepository(BaseRepository[DictInfo]):
    """Repository for DictInfo entity."""

    model = DictInfo


class DictService:
    """
    Dictionary service with Redis read-through cache.

    Features:
    - Read-through cache for dictionary data
    - Cache invalidation on CRUD operations
    - Grouped data by type key and page
    """

    CACHE_NAMESPACE = "dict:data"
    CACHE_TTL = 3600  # 1 hour

    def __init__(self) -> None:
        self.type_repo = DictTypeRepository()
        self.info_repo = DictInfoRepository()

    def _generate_cache_key(self, types: list[str] | None) -> str:
        """Generate cache key based on requested types."""
        if not types:
            return "all"
        types_str = ",".join(sorted(types))
        return hashlib.md5(types_str.encode()).hexdigest()

    async def get_data(
        self, db: AsyncSession, types: list[str] | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get dictionary data with read-through cache.

        Args:
            db: Database session
            types: Optional list of type keys to filter

        Returns:
            Dictionary data grouped by {key}_{page}
        """
        cache_key = self._generate_cache_key(types)

        # Try to get from cache first
        cached = await CacheManager.get(self.CACHE_NAMESPACE, cache_key)
        if cached is not None:
            logger.debug(f"Dict cache hit for key: {cache_key}")
            return cached

        logger.debug(f"Dict cache miss for key: {cache_key}")

        # Fetch from database
        result = await self._fetch_dict_data(db, types)

        # Store in cache
        await CacheManager.set(
            self.CACHE_NAMESPACE, cache_key, result, ttl=self.CACHE_TTL
        )

        return result

    async def _fetch_dict_data(
        self, db: AsyncSession, types: list[str] | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Fetch dictionary data from database.

        Args:
            db: Database session
            types: Optional list of type keys to filter

        Returns:
            Dictionary data grouped by {key}_{page}
        """
        # Fetch dict types
        if types:
            stmt = select(DictType).where(DictType.key.in_(types))
        else:
            stmt = select(DictType)

        type_result = await db.execute(stmt)
        type_data = type_result.scalars().all()

        if not type_data:
            return {}

        # Fetch dict info for these types
        type_ids = [t.id for t in type_data]
        info_stmt = (
            select(DictInfo)
            .where(DictInfo.typeId.in_(type_ids))
            .order_by(DictInfo.orderNum.asc(), DictInfo.createTime.asc())
        )
        info_result = await db.execute(info_stmt)
        info_data = info_result.scalars().all()

        # Group by type key and page
        result: dict[str, list[dict[str, Any]]] = {}
        for type_item in type_data:
            group_key = f"{type_item.key}_{type_item.page}"
            items = [
                info for info in info_data if info.typeId == type_item.id
            ]
            result[group_key] = [
                {
                    "id": item.id,
                    "name": item.name,
                    "typeId": item.typeId,
                    "parentId": item.parentId,
                    "orderNum": item.orderNum,
                    "value": self._parse_value(item.value),
                    "label": type_item.name,
                    "key": group_key,
                }
                for item in items
            ]

        return result

    def _parse_value(self, value: str | None) -> str | int | None:
        """Parse value to int if numeric, otherwise return as string."""
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return value

    async def get_values(
        self, db: AsyncSession, key: str, value: str | list[str]
    ) -> str | list[str | None] | None:
        """
        Get dictionary name(s) by value(s) and type key.

        Args:
            db: Database session
            key: Dictionary type key
            value: Single value or list of values

        Returns:
            Dictionary name(s) corresponding to the value(s)
        """
        # Get dict type
        stmt = select(DictType).where(DictType.key == key)
        result = await db.execute(stmt)
        dict_type = result.scalar_one_or_none()

        if not dict_type:
            return None if isinstance(value, str) else [None] * len(value)

        # Get dict info items
        info_stmt = select(DictInfo).where(DictInfo.typeId == dict_type.id)
        info_result = await db.execute(info_stmt)
        dict_values = info_result.scalars().all()

        if isinstance(value, str):
            return self._find_value_name(value, dict_values)
        else:
            return [self._find_value_name(v, dict_values) for v in value]

    def _find_value_name(
        self, value: str, dict_values: list[DictInfo]
    ) -> str | None:
        """Find dictionary name by value."""
        # Try to match by value first
        for item in dict_values:
            if item.value == value:
                return item.name

        # Try to match by id
        try:
            value_int = int(value)
            for item in dict_values:
                if item.id == value_int:
                    return item.name
        except ValueError:
            pass

        return None

    async def invalidate_cache(self) -> None:
        """Invalidate all dictionary cache."""
        # Delete all keys under the dict namespace
        await CacheManager.delete(self.CACHE_NAMESPACE, "*")
        logger.info("Dict cache invalidated")

    # ==================== Type CRUD ====================

    async def create_type(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> DictType | None:
        """Create a new dictionary type."""
        result = await self.type_repo.create(data, db)
        if result:
            await self.invalidate_cache()
        return result

    async def get_type_by_id(
        self, db: AsyncSession, type_id: int
    ) -> DictType | None:
        """Get dictionary type by ID."""
        return await self.type_repo.get_by_id(type_id, db)

    async def update_type(
        self, db: AsyncSession, type_id: int, data: dict[str, Any]
    ) -> bool:
        """Update dictionary type."""
        result = await self.type_repo.update_by_id(type_id, data, db)
        if result:
            await self.invalidate_cache()
        return result

    async def delete_type(self, db: AsyncSession, type_id: int) -> bool:
        """Delete dictionary type and its items."""
        # Delete related info items first (handled by cascade)
        result = await self.type_repo.delete_by_id(type_id, db)
        if result:
            await self.invalidate_cache()
        return result

    async def list_types(
        self, db: AsyncSession, page: int = 1, size: int = 20
    ) -> dict[str, Any]:
        """List dictionary types with pagination."""
        return await self.type_repo.find_with_pagination(
            db, page=page, size=size, order_by=[("id", "desc")]
        )

    # ==================== Info CRUD ====================

    async def create_info(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> DictInfo | None:
        """Create a new dictionary info item."""
        result = await self.info_repo.create(data, db)
        if result:
            await self.invalidate_cache()
        return result

    async def get_info_by_id(
        self, db: AsyncSession, info_id: int
    ) -> DictInfo | None:
        """Get dictionary info by ID."""
        return await self.info_repo.get_by_id(info_id, db)

    async def update_info(
        self, db: AsyncSession, info_id: int, data: dict[str, Any]
    ) -> bool:
        """Update dictionary info item."""
        result = await self.info_repo.update_by_id(info_id, data, db)
        if result:
            await self.invalidate_cache()
        return result

    async def delete_info(self, db: AsyncSession, info_id: int) -> bool:
        """Delete dictionary info item and its children."""
        # Delete child items recursively
        await self._delete_child_info(db, info_id)

        result = await self.info_repo.delete_by_id(info_id, db)
        if result:
            await self.invalidate_cache()
        return result

    async def _delete_child_info(self, db: AsyncSession, parent_id: int) -> None:
        """Recursively delete child dictionary items."""
        stmt = select(DictInfo).where(DictInfo.parentId == parent_id)
        result = await db.execute(stmt)
        children = result.scalars().all()

        for child in children:
            await self._delete_child_info(db, child.id)
            await db.delete(child)

        await db.flush()

    async def list_info(
        self,
        db: AsyncSession,
        type_id: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """List dictionary info items with pagination."""
        conditions = {}
        if type_id is not None:
            conditions["typeId"] = type_id

        return await self.info_repo.find_with_pagination(
            db,
            conditions=conditions,
            page=page,
            size=size,
            order_by=[("orderNum", "asc"), ("id", "desc")],
        )

    async def list_info_by_type(
        self, db: AsyncSession, type_id: int
    ) -> list[DictInfo]:
        """List all dictionary info items for a type."""
        stmt = (
            select(DictInfo)
            .where(DictInfo.typeId == type_id)
            .order_by(DictInfo.orderNum.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Singleton instance
dict_service = DictService()

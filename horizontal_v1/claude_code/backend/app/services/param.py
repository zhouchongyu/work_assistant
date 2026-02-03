"""
System parameter service with Redis caching.

Provides system parameter management with read-through cache.

Reference:
- cool-admin-midway/src/modules/base/service/sys/param.ts
- Wiki: 后端服务/Python后端服务/控制器层设计/系统参数控制器(SysParam).md
"""

import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.redis import CacheManager
from app.core.repository import BaseRepository
from app.models.sys import BaseSysParam

logger = logging.getLogger("work_assistant.param")


class ParamRepository(BaseRepository[BaseSysParam]):
    """Repository for BaseSysParam entity."""

    model = BaseSysParam


class ParamService:
    """
    System parameter service with Redis caching.

    Features:
    - Read-through cache for parameter values
    - Data type conversion (string, rich text, file list)
    - HTML rendering for rich text parameters
    """

    CACHE_NAMESPACE = "param"
    CACHE_TTL = 3600 * 24  # 24 hours

    def __init__(self) -> None:
        self.repo = ParamRepository()

    async def get_by_key(
        self, db: AsyncSession, key: str
    ) -> str | dict | list | None:
        """
        Get parameter value by key with type conversion.

        Data types:
        - 0: String - parse as JSON if possible, otherwise return string
        - 1: Rich text - return as string
        - 2: File - split by comma to return list

        Args:
            db: Database session
            key: Parameter key

        Returns:
            Converted parameter value
        """
        # Try cache first
        cached = await CacheManager.get(self.CACHE_NAMESPACE, key)
        if cached is not None:
            return self._convert_data(cached)

        # Fetch from database
        stmt = select(BaseSysParam).where(BaseSysParam.keyName == key)
        result = await db.execute(stmt)
        param = result.scalar_one_or_none()

        if not param:
            return None

        # Store in cache
        await CacheManager.set(
            self.CACHE_NAMESPACE,
            key,
            {"data": param.data, "dataType": param.dataType},
            ttl=self.CACHE_TTL,
        )

        return self._convert_data(
            {"data": param.data, "dataType": param.dataType}
        )

    def _convert_data(self, param: dict) -> str | dict | list | None:
        """Convert parameter data based on data type."""
        if not param:
            return None

        data = param.get("data")
        data_type = param.get("dataType", 0)

        if data is None:
            return None

        if data_type == 0:
            # String - try JSON parse first
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        elif data_type == 1:
            # Rich text - return as is
            return data
        elif data_type == 2:
            # File - split by comma
            return data.split(",") if data else []

        return data

    async def get_html_by_key(self, db: AsyncSession, key: str) -> str:
        """
        Get HTML page content by parameter key.

        Used for rendering rich text parameters as HTML page.

        Args:
            db: Database session
            key: Parameter key

        Returns:
            HTML page content
        """
        html_template = "<html><title>@title</title><body>@content</body></html>"

        # Try cache first
        cached = await CacheManager.get(self.CACHE_NAMESPACE, key)
        if cached:
            return html_template.replace(
                "@content", cached.get("data", "")
            ).replace("@title", cached.get("name", ""))

        # Fetch from database
        stmt = select(BaseSysParam).where(BaseSysParam.keyName == key)
        result = await db.execute(stmt)
        param = result.scalar_one_or_none()

        if param:
            return html_template.replace(
                "@content", param.data or ""
            ).replace("@title", param.name or "")

        return html_template.replace("@content", "key notfound").replace(
            "@title", "Not Found"
        )

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> BaseSysParam | None:
        """
        Create a new parameter.

        Validates that keyName is unique.

        Args:
            db: Database session
            data: Parameter data

        Returns:
            Created parameter
        """
        # Check for duplicate keyName
        key_name = data.get("keyName")
        if key_name:
            stmt = select(BaseSysParam).where(
                BaseSysParam.keyName == key_name
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                raise BusinessException("存在相同的keyName")

        param = await self.repo.create(data, db)
        if param:
            await self._refresh_cache(db)
        return param

    async def update(
        self, db: AsyncSession, param_id: int, data: dict[str, Any]
    ) -> bool:
        """
        Update a parameter.

        Validates that keyName is unique (excluding current record).

        Args:
            db: Database session
            param_id: Parameter ID
            data: Update data

        Returns:
            True if successful
        """
        # Check for duplicate keyName
        key_name = data.get("keyName")
        if key_name:
            stmt = select(BaseSysParam).where(
                BaseSysParam.keyName == key_name,
                BaseSysParam.id != param_id,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                raise BusinessException("存在相同的keyName")

        success = await self.repo.update_by_id(param_id, data, db)
        if success:
            await self._refresh_cache(db)
        return success

    async def delete(self, db: AsyncSession, param_id: int) -> bool:
        """Delete a parameter."""
        success = await self.repo.delete_by_id(param_id, db)
        if success:
            await self._refresh_cache(db)
        return success

    async def get_by_id(
        self, db: AsyncSession, param_id: int
    ) -> BaseSysParam | None:
        """Get parameter by ID."""
        return await self.repo.get_by_id(param_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        keyword: str | None = None,
        data_type: int | None = None,
    ) -> dict[str, Any]:
        """List parameters with pagination."""
        conditions = {}
        if data_type is not None:
            conditions["dataType"] = data_type

        # For keyword search, we need custom query
        # The base repository doesn't support LIKE queries directly
        return await self.repo.find_with_pagination(
            db,
            conditions=conditions,
            page=page,
            size=size,
            order_by=[("id", "desc")],
        )

    async def _refresh_cache(self, db: AsyncSession) -> None:
        """
        Refresh all parameter cache.

        Called after any CRUD operation to ensure cache consistency.
        """
        # Fetch all parameters
        stmt = select(BaseSysParam)
        result = await db.execute(stmt)
        params = result.scalars().all()

        # Update cache for each parameter
        for param in params:
            await CacheManager.set(
                self.CACHE_NAMESPACE,
                param.keyName,
                {
                    "data": param.data,
                    "dataType": param.dataType,
                    "name": param.name,
                },
                ttl=self.CACHE_TTL,
            )

        logger.info(f"Param cache refreshed, {len(params)} items")


# Singleton instance
param_service = ParamService()

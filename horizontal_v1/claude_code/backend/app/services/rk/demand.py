"""
Demand service.

Handles demand CRUD and analysis operations.

Reference:
- assistant_py/app/v1/dao/demandDao.py
- Wiki: 后端服务/Python后端服务/后端架构补充/服务层架构/RK业务服务模块.md
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.rk import AnalysisStatus, RkDemand, RkDemandAi, RkDemandCondition

logger = logging.getLogger("work_assistant.rk.demand")


class DemandRepository(BaseRepository[RkDemand]):
    """Repository for RkDemand entity."""

    model = RkDemand


class DemandAiRepository(BaseRepository[RkDemandAi]):
    """Repository for RkDemandAi entity."""

    model = RkDemandAi


class DemandConditionRepository(BaseRepository[RkDemandCondition]):
    """Repository for RkDemandCondition entity."""

    model = RkDemandCondition


class DemandService:
    """
    Demand service.

    Features:
    - Demand CRUD operations
    - Analysis status management
    - Condition management
    """

    def __init__(self) -> None:
        self.repo = DemandRepository()
        self.ai_repo = DemandAiRepository()
        self.condition_repo = DemandConditionRepository()

    # ==================== CRUD Operations ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkDemand | None:
        """Create a new demand record."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, demand_id: int
    ) -> RkDemand | None:
        """Get demand by ID."""
        return await self.repo.get_by_id(demand_id, db)

    async def get_by_ids(
        self, db: AsyncSession, demand_ids: list[int]
    ) -> list[RkDemand]:
        """Get demands by IDs."""
        if not demand_ids:
            return []
        stmt = select(RkDemand).where(RkDemand.id.in_(demand_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, demand_id: int, data: dict[str, Any]
    ) -> bool:
        """Update demand by ID."""
        return await self.repo.update_by_id(demand_id, data, db)

    async def delete(self, db: AsyncSession, demand_id: int) -> bool:
        """Soft delete demand by ID."""
        return await self.repo.soft_delete_by_id(demand_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        conditions: dict[str, Any] | None = None,
        active_only: bool = True,
    ) -> dict[str, Any]:
        """List demands with pagination."""
        cond = conditions or {}
        if active_only:
            cond["active"] = True

        return await self.repo.find_with_pagination(
            db,
            conditions=cond,
            page=page,
            size=size,
            order_by=[("id", "desc")],
        )

    # ==================== Analysis Status ====================

    async def update_analysis_status(
        self,
        db: AsyncSession,
        demand_id: int,
        status: str,
    ) -> None:
        """Update demand analysis status."""
        await self.repo.update_by_id(demand_id, {"analysis_status": status}, db)
        await db.commit()

        # TODO: Send MQTT notification
        logger.info(f"Demand {demand_id} analysis status updated to {status}")

    async def increment_version(
        self, db: AsyncSession, demand_id: int
    ) -> int:
        """Increment demand version and return new version."""
        demand = await self.get_by_id(db, demand_id)
        if not demand:
            return 0
        new_version = (demand.version or 1) + 1
        await self.update(db, demand_id, {"version": new_version})
        return new_version

    # ==================== AI Data ====================

    async def get_ai_data(
        self, db: AsyncSession, demand_id: int
    ) -> RkDemandAi | None:
        """Get demand AI data."""
        stmt = select(RkDemandAi).where(RkDemandAi.demandId == demand_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_ai_data(
        self, db: AsyncSession, demand_id: int, data: dict[str, Any]
    ) -> RkDemandAi:
        """Save or update demand AI data."""
        existing = await self.get_ai_data(db, demand_id)
        if existing:
            existing.data = data
            await db.flush()
            return existing
        else:
            return await self.ai_repo.create(
                {"demandId": demand_id, "data": data}, db
            )

    # ==================== Conditions ====================

    async def get_conditions(
        self, db: AsyncSession, demand_id: int
    ) -> list[RkDemandCondition]:
        """Get conditions for demand."""
        stmt = select(RkDemandCondition).where(
            RkDemandCondition.demandId == demand_id
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def save_conditions(
        self,
        db: AsyncSession,
        demand_id: int,
        conditions: list[dict[str, Any]],
    ) -> None:
        """Save conditions for demand (replace all)."""
        # Delete existing conditions
        existing = await self.get_conditions(db, demand_id)
        for cond in existing:
            await db.delete(cond)

        # Add new conditions
        for cond in conditions:
            await self.condition_repo.create(
                {
                    "demandId": demand_id,
                    "conditionKey": cond.get("key"),
                    "conditionValue": cond.get("value"),
                },
                db,
            )

    # ==================== Search ====================

    async def search_by_customer(
        self,
        db: AsyncSession,
        customer_id: int,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """Search demands by customer ID."""
        return await self.list_with_pagination(
            db,
            page=page,
            size=size,
            conditions={"customerId": customer_id},
        )


# Singleton instance
demand_service = DemandService()

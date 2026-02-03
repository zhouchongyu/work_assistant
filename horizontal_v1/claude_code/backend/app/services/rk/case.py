"""
Case (Supply-Demand Link) service.

Handles case management with status machine logic.

Reference:
- assistant_py/app/v1/service/caseService.py
- Wiki: 数据管理/实体模型/核心业务实体/案例实体(Case).md
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.repository import BaseRepository
from app.models.rk import (
    CASE_INIT_LEVEL,
    CASE_STATUS_LEVEL,
    RkCase,
    RkCaseStatus,
    RkMatchResult,
)

logger = logging.getLogger("work_assistant.rk.case")


class CaseRepository(BaseRepository[RkCase]):
    """Repository for RkCase entity."""

    model = RkCase


class CaseStatusRepository(BaseRepository[RkCaseStatus]):
    """Repository for RkCaseStatus entity."""

    model = RkCaseStatus


class MatchResultRepository(BaseRepository[RkMatchResult]):
    """Repository for RkMatchResult entity."""

    model = RkMatchResult


class CaseService:
    """
    Case (Supply-Demand Link) service.

    Features:
    - Case CRUD operations
    - Status machine logic
    - Status history tracking
    """

    def __init__(self) -> None:
        self.repo = CaseRepository()
        self.status_repo = CaseStatusRepository()
        self.match_repo = MatchResultRepository()

    # ==================== CRUD Operations ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkCase | None:
        """Create a new case."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, case_id: int
    ) -> RkCase | None:
        """Get case by ID."""
        return await self.repo.get_by_id(case_id, db)

    async def get_by_supply_demand(
        self, db: AsyncSession, supply_id: int, demand_id: int
    ) -> RkCase | None:
        """Get case by supply and demand IDs."""
        stmt = select(RkCase).where(
            RkCase.supplyId == supply_id,
            RkCase.demandId == demand_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, case_id: int, data: dict[str, Any]
    ) -> bool:
        """Update case by ID."""
        return await self.repo.update_by_id(case_id, data, db)

    async def delete(self, db: AsyncSession, case_id: int) -> bool:
        """Soft delete case by ID."""
        return await self.repo.soft_delete_by_id(case_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        conditions: dict[str, Any] | None = None,
        active_only: bool = True,
    ) -> dict[str, Any]:
        """List cases with pagination."""
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

    # ==================== Status Machine ====================

    def get_status_level(self, status: str) -> int:
        """Get numeric level for status."""
        return CASE_STATUS_LEVEL.get(status, CASE_INIT_LEVEL)

    def validate_status_transition(
        self, current_status: str | None, new_status: str
    ) -> bool:
        """
        Validate if status transition is allowed.

        Generally, status can only move forward or stay the same.
        Special cases may allow backward movement with proper authorization.
        """
        if not current_status:
            return True

        current_level = self.get_status_level(current_status)
        new_level = self.get_status_level(new_status)

        # Allow forward or same level
        return new_level >= current_level

    async def update_status(
        self,
        db: AsyncSession,
        case_id: int,
        new_status: str,
        remark: str | None = None,
        force: bool = False,
    ) -> bool:
        """
        Update case status with validation.

        Args:
            db: Database session
            case_id: Case ID
            new_status: New status value
            remark: Optional remark for status change
            force: Force status update without validation

        Returns:
            True if successful

        Raises:
            BusinessException: If status transition is invalid
        """
        case = await self.get_by_id(db, case_id)
        if not case:
            raise BusinessException("Case not found")

        current_status = case.supplyDemandStatus3

        if not force and not self.validate_status_transition(
            current_status, new_status
        ):
            raise BusinessException(
                f"Invalid status transition from {current_status} to {new_status}"
            )

        # Update case status
        await self.update(db, case_id, {"supplyDemandStatus3": new_status})

        # Record status history
        await self.add_status_record(db, case_id, new_status, remark)

        logger.info(
            f"Case {case_id} status updated: {current_status} -> {new_status}"
        )

        # TODO: Send MQTT notification for status change

        return True

    # ==================== Status History ====================

    async def add_status_record(
        self,
        db: AsyncSession,
        case_id: int,
        status: str,
        remark: str | None = None,
    ) -> RkCaseStatus | None:
        """Add a status history record."""
        return await self.status_repo.create(
            {
                "case_id": case_id,
                "status": status,
                "remark": remark or "",
                "active": True,
            },
            db,
        )

    async def get_status_history(
        self, db: AsyncSession, case_id: int
    ) -> list[RkCaseStatus]:
        """Get status history for case."""
        stmt = (
            select(RkCaseStatus)
            .where(RkCaseStatus.case_id == case_id)
            .order_by(RkCaseStatus.createTime.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ==================== Match Results ====================

    async def get_match_result(
        self, db: AsyncSession, supply_id: int, demand_id: int
    ) -> RkMatchResult | None:
        """Get match result for supply-demand pair."""
        stmt = select(RkMatchResult).where(
            RkMatchResult.supply_id == supply_id,
            RkMatchResult.demand_id == demand_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_match_result(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkMatchResult:
        """Save or update match result."""
        supply_id = data.get("supply_id")
        demand_id = data.get("demand_id")

        existing = await self.get_match_result(db, supply_id, demand_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await db.flush()
            return existing
        else:
            return await self.match_repo.create(data, db)

    async def get_match_results_by_demand(
        self, db: AsyncSession, demand_id: int
    ) -> list[RkMatchResult]:
        """Get all match results for a demand."""
        stmt = (
            select(RkMatchResult)
            .where(RkMatchResult.demand_id == demand_id)
            .order_by(RkMatchResult.score.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete_match_results_by_supply(
        self, db: AsyncSession, supply_id: int
    ) -> None:
        """Delete all match results for a supply."""
        stmt = select(RkMatchResult).where(RkMatchResult.supply_id == supply_id)
        result = await db.execute(stmt)
        for match in result.scalars().all():
            await db.delete(match)

    # ==================== Search ====================

    async def search_by_supply(
        self,
        db: AsyncSession,
        supply_id: int,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """Search cases by supply ID."""
        return await self.list_with_pagination(
            db,
            page=page,
            size=size,
            conditions={"supplyId": supply_id},
        )

    async def search_by_demand(
        self,
        db: AsyncSession,
        demand_id: int,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """Search cases by demand ID."""
        return await self.list_with_pagination(
            db,
            page=page,
            size=size,
            conditions={"demandId": demand_id},
        )


# Singleton instance
case_service = CaseService()

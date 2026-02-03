"""
Supply (Resume) service.

Handles resume upload, analysis triggering, and CRUD operations.

Reference:
- assistant_py/app/v1/service/supplyService.py
- Wiki: 后端服务/Python后端服务/后端架构补充/服务层架构/RK业务服务模块.md
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.rk import AnalysisStatus, RkSupply, RkSupplyAi, RkSupplyEditRecord

logger = logging.getLogger("work_assistant.rk.supply")


class SupplyRepository(BaseRepository[RkSupply]):
    """Repository for RkSupply entity."""

    model = RkSupply


class SupplyAiRepository(BaseRepository[RkSupplyAi]):
    """Repository for RkSupplyAi entity."""

    model = RkSupplyAi


class SupplyEditRecordRepository(BaseRepository[RkSupplyEditRecord]):
    """Repository for RkSupplyEditRecord entity."""

    model = RkSupplyEditRecord


class SupplyService:
    """
    Supply (Resume) service.

    Features:
    - Resume CRUD operations
    - Analysis status management
    - Edit record tracking
    """

    def __init__(self) -> None:
        self.repo = SupplyRepository()
        self.ai_repo = SupplyAiRepository()
        self.edit_repo = SupplyEditRecordRepository()

    # ==================== CRUD Operations ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkSupply | None:
        """Create a new supply record."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, supply_id: int
    ) -> RkSupply | None:
        """Get supply by ID."""
        return await self.repo.get_by_id(supply_id, db)

    async def get_by_ids(
        self, db: AsyncSession, supply_ids: list[int]
    ) -> list[RkSupply]:
        """Get supplies by IDs."""
        if not supply_ids:
            return []
        stmt = select(RkSupply).where(RkSupply.id.in_(supply_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(
        self, db: AsyncSession, code: str
    ) -> RkSupply | None:
        """Get supply by code."""
        stmt = select(RkSupply).where(RkSupply.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, supply_id: int, data: dict[str, Any]
    ) -> bool:
        """Update supply by ID."""
        return await self.repo.update_by_id(supply_id, data, db)

    async def delete(self, db: AsyncSession, supply_id: int) -> bool:
        """Soft delete supply by ID."""
        return await self.repo.soft_delete_by_id(supply_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        conditions: dict[str, Any] | None = None,
        active_only: bool = True,
    ) -> dict[str, Any]:
        """List supplies with pagination."""
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
        supply_id: int,
        status: str,
    ) -> None:
        """
        Update supply analysis status.

        Args:
            db: Database session
            supply_id: Supply ID
            status: Analysis status (from AnalysisStatus enum)
        """
        if status in [
            AnalysisStatus.CONTACT_ANALYSIS_START.value,
            AnalysisStatus.CONTACT_ANALYSIS_DONE.value,
            AnalysisStatus.CONTACT_ANALYSIS_ERROR.value,
        ]:
            update_data = {"contact_analysis_status": status}
        else:
            update_data = {"analysis_status": status}

        await self.repo.update_by_id(supply_id, update_data, db)
        await db.commit()

        # TODO: Send MQTT notification
        logger.info(f"Supply {supply_id} analysis status updated to {status}")

    async def increment_version(
        self, db: AsyncSession, supply_id: int
    ) -> int:
        """Increment supply version and return new version."""
        supply = await self.get_by_id(db, supply_id)
        if not supply:
            return 0
        new_version = (supply.version or 1) + 1
        await self.update(db, supply_id, {"version": new_version})
        return new_version

    # ==================== AI Data ====================

    async def get_ai_data(
        self, db: AsyncSession, supply_id: int
    ) -> RkSupplyAi | None:
        """Get supply AI data."""
        stmt = select(RkSupplyAi).where(RkSupplyAi.supplyId == supply_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_ai_data(
        self, db: AsyncSession, supply_id: int, data: dict[str, Any]
    ) -> RkSupplyAi:
        """Save or update supply AI data."""
        existing = await self.get_ai_data(db, supply_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await db.flush()
            return existing
        else:
            data["supplyId"] = supply_id
            return await self.ai_repo.create(data, db)

    # ==================== Edit Records ====================

    async def add_edit_record(
        self,
        db: AsyncSession,
        supply_id: int,
        user_id: int | None,
        field_name: str,
        old_value: str | None,
        new_value: str | None,
        remark: str | None = None,
    ) -> RkSupplyEditRecord | None:
        """Add an edit record for supply."""
        return await self.edit_repo.create(
            {
                "supplyId": supply_id,
                "userId": user_id,
                "fieldName": field_name,
                "oldValue": old_value,
                "newValue": new_value,
                "remark": remark,
            },
            db,
        )

    async def get_edit_records(
        self, db: AsyncSession, supply_id: int
    ) -> list[RkSupplyEditRecord]:
        """Get edit records for supply."""
        stmt = (
            select(RkSupplyEditRecord)
            .where(RkSupplyEditRecord.supplyId == supply_id)
            .order_by(RkSupplyEditRecord.createTime.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ==================== Search ====================

    async def search_by_vendor(
        self,
        db: AsyncSession,
        vendor_id: int,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """Search supplies by vendor ID."""
        return await self.list_with_pagination(
            db,
            page=page,
            size=size,
            conditions={"vendorId": vendor_id},
        )


# Singleton instance
supply_service = SupplyService()

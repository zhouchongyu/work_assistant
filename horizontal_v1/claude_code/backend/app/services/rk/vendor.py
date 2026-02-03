"""
Vendor service.

Handles vendor and vendor contact management.

Reference:
- assistant_py/app/v1/dao/vendorDao.py
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.rk import RkVendor, RkVendorContact

logger = logging.getLogger("work_assistant.rk.vendor")


class VendorRepository(BaseRepository[RkVendor]):
    """Repository for RkVendor entity."""

    model = RkVendor


class VendorContactRepository(BaseRepository[RkVendorContact]):
    """Repository for RkVendorContact entity."""

    model = RkVendorContact


class VendorService:
    """
    Vendor service.

    Features:
    - Vendor CRUD operations
    - Vendor contact management
    - SharePoint folder management
    """

    def __init__(self) -> None:
        self.repo = VendorRepository()
        self.contact_repo = VendorContactRepository()

    # ==================== Vendor CRUD ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkVendor | None:
        """Create a new vendor."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, vendor_id: int
    ) -> RkVendor | None:
        """Get vendor by ID."""
        return await self.repo.get_by_id(vendor_id, db)

    async def update(
        self, db: AsyncSession, vendor_id: int, data: dict[str, Any]
    ) -> bool:
        """Update vendor by ID."""
        return await self.repo.update_by_id(vendor_id, data, db)

    async def delete(self, db: AsyncSession, vendor_id: int) -> bool:
        """Soft delete vendor by ID."""
        return await self.repo.soft_delete_by_id(vendor_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        conditions: dict[str, Any] | None = None,
        active_only: bool = True,
    ) -> dict[str, Any]:
        """List vendors with pagination."""
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

    # ==================== Contact CRUD ====================

    async def create_contact(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkVendorContact | None:
        """Create a new vendor contact."""
        return await self.contact_repo.create(data, db)

    async def get_contact_by_id(
        self, db: AsyncSession, contact_id: int
    ) -> RkVendorContact | None:
        """Get vendor contact by ID."""
        return await self.contact_repo.get_by_id(contact_id, db)

    async def update_contact(
        self, db: AsyncSession, contact_id: int, data: dict[str, Any]
    ) -> bool:
        """Update vendor contact by ID."""
        return await self.contact_repo.update_by_id(contact_id, data, db)

    async def delete_contact(
        self, db: AsyncSession, contact_id: int
    ) -> bool:
        """Soft delete vendor contact by ID."""
        return await self.contact_repo.soft_delete_by_id(contact_id, db)

    async def get_contacts_by_vendor(
        self, db: AsyncSession, vendor_id: int
    ) -> list[RkVendorContact]:
        """Get all contacts for a vendor."""
        stmt = (
            select(RkVendorContact)
            .where(
                RkVendorContact.vendorId == vendor_id,
                RkVendorContact.active == True,
            )
            .order_by(RkVendorContact.default.desc(), RkVendorContact.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_default_contact(
        self, db: AsyncSession, vendor_id: int
    ) -> RkVendorContact | None:
        """Get default contact for a vendor."""
        stmt = select(RkVendorContact).where(
            RkVendorContact.vendorId == vendor_id,
            RkVendorContact.default == True,
            RkVendorContact.active == True,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # ==================== SharePoint Integration ====================

    async def update_folder_info(
        self,
        db: AsyncSession,
        vendor_id: int,
        folder_id: str,
        folder_url: str,
    ) -> bool:
        """Update vendor's SharePoint folder info."""
        return await self.update(
            db,
            vendor_id,
            {
                "folderId": folder_id,
                "folderUrl": folder_url,
            },
        )

    async def update_delta_link(
        self, db: AsyncSession, vendor_id: int, delta_link: str
    ) -> bool:
        """Update vendor's delta link for incremental sync."""
        return await self.update(
            db,
            vendor_id,
            {"deltaLink": delta_link},
        )


# Singleton instance
vendor_service = VendorService()

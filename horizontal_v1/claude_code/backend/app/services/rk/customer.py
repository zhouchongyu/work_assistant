"""
Customer service.

Handles customer and customer contact management.

Reference:
- assistant_py/app/v1/dao/customerDao.py
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.rk import RkCustomer, RkCustomerContact

logger = logging.getLogger("work_assistant.rk.customer")


class CustomerRepository(BaseRepository[RkCustomer]):
    """Repository for RkCustomer entity."""

    model = RkCustomer


class CustomerContactRepository(BaseRepository[RkCustomerContact]):
    """Repository for RkCustomerContact entity."""

    model = RkCustomerContact


class CustomerService:
    """
    Customer service.

    Features:
    - Customer CRUD operations
    - Customer contact management
    """

    def __init__(self) -> None:
        self.repo = CustomerRepository()
        self.contact_repo = CustomerContactRepository()

    # ==================== Customer CRUD ====================

    async def create(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> RkCustomer | None:
        """Create a new customer."""
        return await self.repo.create(data, db)

    async def get_by_id(
        self, db: AsyncSession, customer_id: int
    ) -> RkCustomer | None:
        """Get customer by ID."""
        return await self.repo.get_by_id(customer_id, db)

    async def update(
        self, db: AsyncSession, customer_id: int, data: dict[str, Any]
    ) -> bool:
        """Update customer by ID."""
        return await self.repo.update_by_id(customer_id, data, db)

    async def delete(self, db: AsyncSession, customer_id: int) -> bool:
        """Soft delete customer by ID."""
        return await self.repo.soft_delete_by_id(customer_id, db)

    async def list_with_pagination(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        conditions: dict[str, Any] | None = None,
        active_only: bool = True,
    ) -> dict[str, Any]:
        """List customers with pagination."""
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
    ) -> RkCustomerContact | None:
        """Create a new customer contact."""
        return await self.contact_repo.create(data, db)

    async def get_contact_by_id(
        self, db: AsyncSession, contact_id: int
    ) -> RkCustomerContact | None:
        """Get customer contact by ID."""
        return await self.contact_repo.get_by_id(contact_id, db)

    async def update_contact(
        self, db: AsyncSession, contact_id: int, data: dict[str, Any]
    ) -> bool:
        """Update customer contact by ID."""
        return await self.contact_repo.update_by_id(contact_id, data, db)

    async def delete_contact(
        self, db: AsyncSession, contact_id: int
    ) -> bool:
        """Soft delete customer contact by ID."""
        return await self.contact_repo.soft_delete_by_id(contact_id, db)

    async def get_contacts_by_customer(
        self, db: AsyncSession, customer_id: int
    ) -> list[RkCustomerContact]:
        """Get all contacts for a customer."""
        stmt = (
            select(RkCustomerContact)
            .where(
                RkCustomerContact.customerId == customer_id,
                RkCustomerContact.active == True,
            )
            .order_by(RkCustomerContact.default.desc(), RkCustomerContact.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_default_contact(
        self, db: AsyncSession, customer_id: int
    ) -> RkCustomerContact | None:
        """Get default contact for a customer."""
        stmt = select(RkCustomerContact).where(
            RkCustomerContact.customerId == customer_id,
            RkCustomerContact.default == True,
            RkCustomerContact.active == True,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# Singleton instance
customer_service = CustomerService()

"""
Generic CRUD repository base class.

Provides common database operations for all entities.

Reference:
- assistant_py/app/v1/dao/supplyDao.py: Original DAO pattern
- Wiki: 数据管理/数据访问层/DAO基础模式.md
"""

from datetime import datetime
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base

# Type variable for the model class
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic CRUD repository with common database operations.

    Usage:
        class SupplyRepository(BaseRepository[SupplyEntity]):
            model = SupplyEntity

        # In service
        repo = SupplyRepository()
        supply = await repo.get_by_id(1, db)
    """

    model: type[ModelType]

    # ==================== Create Operations ====================

    async def create(
        self,
        data: dict[str, Any],
        db: AsyncSession,
    ) -> ModelType | None:
        """
        Create a new record.

        Args:
            data: Dictionary of field values
            db: Database session

        Returns:
            Created entity or None
        """
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_many(
        self,
        data_list: list[dict[str, Any]],
        db: AsyncSession,
    ) -> Sequence[ModelType]:
        """
        Create multiple records.

        Args:
            data_list: List of dictionaries with field values
            db: Database session

        Returns:
            List of created entities
        """
        if not data_list:
            return []
        stmt = insert(self.model).values(data_list).returning(self.model)
        result = await db.execute(stmt)
        return result.scalars().all()

    # ==================== Read Operations ====================

    async def get_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
        load_relations: list[str] | None = None,
    ) -> ModelType | None:
        """
        Get a single record by ID.

        Args:
            pk_id: Primary key ID
            db: Database session
            load_relations: Optional list of relationships to eager load

        Returns:
            Entity or None if not found
        """
        stmt = select(self.model).where(self.model.id == pk_id)

        if load_relations:
            for relation in load_relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        pk_ids: list[int],
        db: AsyncSession,
    ) -> Sequence[ModelType]:
        """
        Get multiple records by IDs.

        Args:
            pk_ids: List of primary key IDs
            db: Database session

        Returns:
            List of entities
        """
        if not pk_ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(pk_ids))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        db: AsyncSession,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ModelType]:
        """
        Get all records with optional pagination.

        Args:
            db: Database session
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of entities
        """
        stmt = select(self.model)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_field(
        self,
        field_name: str,
        value: Any,
        db: AsyncSession,
    ) -> Sequence[ModelType]:
        """
        Get records by a single field value.

        Args:
            field_name: Name of the field to filter by
            value: Value to match
            db: Database session

        Returns:
            List of matching entities
        """
        field = getattr(self.model, field_name, None)
        if field is None:
            raise ValueError(f"Invalid field name: {field_name}")

        stmt = select(self.model).where(field == value)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_one_by_field(
        self,
        field_name: str,
        value: Any,
        db: AsyncSession,
    ) -> ModelType | None:
        """
        Get a single record by a field value.

        Args:
            field_name: Name of the field to filter by
            value: Value to match
            db: Database session

        Returns:
            Entity or None if not found
        """
        field = getattr(self.model, field_name, None)
        if field is None:
            raise ValueError(f"Invalid field name: {field_name}")

        stmt = select(self.model).where(field == value).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(
        self,
        pk_id: int,
        db: AsyncSession,
    ) -> bool:
        """
        Check if a record exists.

        Args:
            pk_id: Primary key ID
            db: Database session

        Returns:
            True if exists, False otherwise
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.id == pk_id)
        result = await db.execute(stmt)
        count = result.scalar()
        return count > 0 if count else False

    async def count(
        self,
        db: AsyncSession,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Count records with optional filters.

        Args:
            db: Database session
            filters: Optional dictionary of field filters

        Returns:
            Number of matching records
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for field_name, value in filters.items():
                field = getattr(self.model, field_name, None)
                if field is not None:
                    stmt = stmt.where(field == value)

        result = await db.execute(stmt)
        return result.scalar() or 0

    # ==================== Update Operations ====================

    async def update_by_id(
        self,
        pk_id: int,
        data: dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """
        Update a record by ID.

        Args:
            pk_id: Primary key ID
            data: Dictionary of field values to update
            db: Database session

        Returns:
            True if updated, False if not found
        """
        stmt = update(self.model).where(self.model.id == pk_id).values(**data)
        result = await db.execute(stmt)
        return result.rowcount > 0

    async def update_by_id_returning(
        self,
        pk_id: int,
        data: dict[str, Any],
        db: AsyncSession,
    ) -> ModelType | None:
        """
        Update a record by ID and return the updated entity.

        Args:
            pk_id: Primary key ID
            data: Dictionary of field values to update
            db: Database session

        Returns:
            Updated entity or None if not found
        """
        stmt = (
            update(self.model)
            .where(self.model.id == pk_id)
            .values(**data)
            .returning(self.model)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_many(
        self,
        pk_ids: list[int],
        data: dict[str, Any],
        db: AsyncSession,
    ) -> int:
        """
        Update multiple records by IDs.

        Args:
            pk_ids: List of primary key IDs
            data: Dictionary of field values to update
            db: Database session

        Returns:
            Number of updated records
        """
        if not pk_ids:
            return 0
        stmt = update(self.model).where(self.model.id.in_(pk_ids)).values(**data)
        result = await db.execute(stmt)
        return result.rowcount

    # ==================== Delete Operations ====================

    async def delete_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
    ) -> bool:
        """
        Delete a record by ID.

        Args:
            pk_id: Primary key ID
            db: Database session

        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == pk_id)
        result = await db.execute(stmt)
        return result.rowcount > 0

    async def delete_many(
        self,
        pk_ids: list[int],
        db: AsyncSession,
    ) -> int:
        """
        Delete multiple records by IDs.

        Args:
            pk_ids: List of primary key IDs
            db: Database session

        Returns:
            Number of deleted records
        """
        if not pk_ids:
            return 0
        stmt = delete(self.model).where(self.model.id.in_(pk_ids))
        result = await db.execute(stmt)
        return result.rowcount

    # ==================== Soft Delete Operations ====================

    async def soft_delete_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
        deleted_by: int | None = None,
    ) -> bool:
        """
        Soft delete a record by ID (sets deletedAt timestamp).

        Requires the model to have SoftDeleteMixin.

        Args:
            pk_id: Primary key ID
            db: Database session
            deleted_by: User ID who performed the deletion

        Returns:
            True if soft deleted, False if not found
        """
        data: dict[str, Any] = {"deletedAt": datetime.now()}
        if deleted_by and hasattr(self.model, "updatedBy"):
            data["updatedBy"] = deleted_by
        return await self.update_by_id(pk_id, data, db)

    async def restore_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
    ) -> bool:
        """
        Restore a soft-deleted record.

        Args:
            pk_id: Primary key ID
            db: Database session

        Returns:
            True if restored, False if not found
        """
        return await self.update_by_id(pk_id, {"deletedAt": None}, db)

    # ==================== Active Flag Operations ====================

    async def get_all_active(
        self,
        db: AsyncSession,
    ) -> Sequence[ModelType]:
        """
        Get all active records (where active=True).

        Requires the model to have BusinessBase mixin.

        Args:
            db: Database session

        Returns:
            List of active entities
        """
        if not hasattr(self.model, "active"):
            raise ValueError("Model does not have 'active' field")

        stmt = select(self.model).where(self.model.active == True)  # noqa: E712
        result = await db.execute(stmt)
        return result.scalars().all()

    async def deactivate_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
        reason: str | None = None,
    ) -> bool:
        """
        Deactivate a record (set active=False).

        Args:
            pk_id: Primary key ID
            db: Database session
            reason: Optional reason for deactivation

        Returns:
            True if deactivated, False if not found
        """
        data: dict[str, Any] = {"active": False}
        if reason and hasattr(self.model, "reason"):
            data["reason"] = reason
        return await self.update_by_id(pk_id, data, db)

    async def activate_by_id(
        self,
        pk_id: int,
        db: AsyncSession,
    ) -> bool:
        """
        Activate a record (set active=True).

        Args:
            pk_id: Primary key ID
            db: Database session

        Returns:
            True if activated, False if not found
        """
        return await self.update_by_id(pk_id, {"active": True, "reason": None}, db)

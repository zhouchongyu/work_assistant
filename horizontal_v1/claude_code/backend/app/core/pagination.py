"""
Pagination utilities for list queries.

Provides standardized pagination for all list endpoints.

Reference:
- Wiki: API参考文档/API参考文档.md
- cool-admin-midway pagination pattern
"""

from dataclasses import dataclass
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class PageParams:
    """Pagination parameters."""

    page: int = 1
    size: int = 20
    order: str | None = None
    sort: str = "desc"

    def __post_init__(self) -> None:
        """Validate and normalize pagination parameters."""
        if self.page < 1:
            self.page = 1
        if self.size < 1:
            self.size = 1
        if self.size > 100:
            self.size = 100
        if self.sort not in ("asc", "desc"):
            self.sort = "desc"

    @property
    def offset(self) -> int:
        """Calculate offset for SQL query."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get limit (alias for size)."""
        return self.size


@dataclass
class PageResult(Generic[T]):
    """Paginated result wrapper."""

    list: Sequence[T]
    pagination: dict[str, Any]

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        page: int,
        size: int,
    ) -> "PageResult[T]":
        """
        Create a paginated result.

        Args:
            items: List of items
            total: Total count of items
            page: Current page number
            size: Page size

        Returns:
            PageResult instance
        """
        return cls(
            list=items,
            pagination={
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size if size > 0 else 0,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "list": self.list,
            "pagination": self.pagination,
        }


async def paginate(
    query: Select,
    db: AsyncSession,
    params: PageParams,
    order_column: Any | None = None,
) -> PageResult:
    """
    Execute a paginated query.

    Args:
        query: SQLAlchemy select query
        db: Database session
        params: Pagination parameters
        order_column: Optional column to order by (overrides params.order)

    Returns:
        PageResult with items and pagination info

    Usage:
        stmt = select(SupplyEntity).where(SupplyEntity.active == True)
        result = await paginate(stmt, db, PageParams(page=1, size=20))
    """
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply ordering
    if order_column is not None:
        if params.sort == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

    # Apply pagination
    query = query.offset(params.offset).limit(params.limit)

    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()

    return PageResult.create(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
    )


async def paginate_with_model(
    model: type,
    db: AsyncSession,
    params: PageParams,
    filters: dict[str, Any] | None = None,
    order_field: str | None = None,
) -> PageResult:
    """
    Paginate a model with optional filters.

    Args:
        model: SQLAlchemy model class
        db: Database session
        params: Pagination parameters
        filters: Optional dictionary of field filters
        order_field: Optional field name to order by

    Returns:
        PageResult with items and pagination info

    Usage:
        result = await paginate_with_model(
            SupplyEntity,
            db,
            PageParams(page=1, size=20),
            filters={"active": True, "vendorId": 123},
            order_field="createTime",
        )
    """
    query = select(model)

    # Apply filters
    if filters:
        for field_name, value in filters.items():
            field = getattr(model, field_name, None)
            if field is not None:
                if isinstance(value, (list, tuple)):
                    query = query.where(field.in_(value))
                elif value is None:
                    query = query.where(field.is_(None))
                else:
                    query = query.where(field == value)

    # Determine order column
    order_column = None
    if order_field:
        order_column = getattr(model, order_field, None)
    elif params.order:
        order_column = getattr(model, params.order, None)

    # Default to id if no order specified
    if order_column is None and hasattr(model, "id"):
        order_column = model.id

    return await paginate(query, db, params, order_column)


def page_params_from_dict(data: dict[str, Any]) -> PageParams:
    """
    Create PageParams from a dictionary.

    Args:
        data: Dictionary with page, size, order, sort keys

    Returns:
        PageParams instance
    """
    return PageParams(
        page=int(data.get("page", 1)),
        size=int(data.get("size", 20)),
        order=data.get("order"),
        sort=data.get("sort", "desc"),
    )

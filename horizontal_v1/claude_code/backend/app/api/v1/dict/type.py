"""
Dictionary type API endpoints.

Provides CRUD operations for dictionary types.

Reference:
- cool-admin-midway/src/modules/dict/controller/admin/type.ts
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.schemas.dict import DictTypeCreate, DictTypeUpdate
from app.services.dict import dict_service

router = APIRouter(prefix="/type", tags=["DictType"])


@router.post("/add", response_model=None)
async def add_type(
    data: DictTypeCreate,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Create a new dictionary type.
    """
    result = await dict_service.create_type(db, data.model_dump())
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_type(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Delete dictionary types by IDs.
    """
    for type_id in ids:
        await dict_service.delete_type(db, type_id)
    return success()


@router.post("/update", response_model=None)
async def update_type(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Update a dictionary type.
    """
    type_id = data.pop("id", None)
    if not type_id:
        return success(result=None)

    await dict_service.update_type(db, type_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_type_info(
    id: int = Query(..., description="Dictionary type ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get dictionary type by ID.
    """
    result = await dict_service.get_type_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_types(
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    List all dictionary types (no pagination).
    """
    result = await dict_service.list_types(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_types(
    page: int = 1,
    size: int = 20,
    keyWord: str | None = None,
    key: str | None = None,
    keyLike: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get dictionary types with pagination.
    """
    result = await dict_service.list_types(db, page=page, size=size)
    return success(result=result)

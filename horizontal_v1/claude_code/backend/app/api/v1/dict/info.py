"""
Dictionary info API endpoints.

Provides CRUD operations for dictionary items and data retrieval.

Reference:
- cool-admin-midway/src/modules/dict/controller/admin/info.ts
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.models import to_dict
from app.schemas.dict import DictInfoCreate, DictInfoUpdate
from app.services.dict import dict_service

router = APIRouter(prefix="/info", tags=["DictInfo"])


@router.post("/add", response_model=None)
async def add_info(
    data: DictInfoCreate,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Create a new dictionary info item.
    """
    result = await dict_service.create_info(db, data.model_dump())
    if result:
        return success(result={"id": result.id})
    return success(result=None)


@router.post("/delete", response_model=None)
async def delete_info(
    ids: list[int],
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Delete dictionary info items by IDs.
    """
    for info_id in ids:
        await dict_service.delete_info(db, info_id)
    return success()


@router.post("/update", response_model=None)
async def update_info(
    data: dict,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Update a dictionary info item.
    """
    info_id = data.pop("id", None)
    if not info_id:
        return success(result=None)

    await dict_service.update_info(db, info_id, data)
    return success()


@router.post("/info", response_model=None)
async def get_info_detail(
    id: int = Query(..., description="Dictionary info ID"),
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get dictionary info by ID.
    """
    result = await dict_service.get_info_by_id(db, id)
    if result:
        return success(result=to_dict(result))
    return success(result=None)


@router.post("/list", response_model=None)
async def list_info(
    typeId: int | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    List dictionary info items (no pagination).
    """
    if typeId:
        result = await dict_service.list_info_by_type(db, typeId)
        return success(result=[to_dict(item) for item in result])
    result = await dict_service.list_info(db, page=1, size=1000)
    return success(result=result.get("list", []))


@router.post("/page", response_model=None)
async def page_info(
    page: int = 1,
    size: int = 20,
    typeId: int | None = None,
    keyWord: str | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get dictionary info items with pagination.
    """
    result = await dict_service.list_info(db, type_id=typeId, page=page, size=size)
    return success(result=result)


@router.post("/data", response_model=None)
async def get_dict_data(
    types: list[str] | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Get dictionary data grouped by type key and page.

    This endpoint supports Redis read-through cache for performance.
    Data is cached for 1 hour and automatically invalidated on updates.
    """
    result = await dict_service.get_data(db, types)
    return success(result=result)

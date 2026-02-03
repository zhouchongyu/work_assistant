from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.sharepoint_graph.client import GraphClient, get_graph_client
from backend.app.models.rk_vendor import RkVendor
from backend.app.schemas.rk_vendor import RkVendorCreateRequest, RkVendorOut, RkVendorUpdateRequest

router = APIRouter(prefix="/rk/vendor", tags=["rk"])


@router.post("/add")
async def add_vendor(
    payload: RkVendorCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    vendor = RkVendor(
        name=payload.name,
        code=payload.code,
        created_by=int(current.user.id),
        updated_by=int(current.user.id),
        owner_id=int(current.user.id),
        department_id=current.user.department_id,
        active=True,
        to_be_confirmed=False,
    )
    session.add(vendor)
    await session.flush()

    folder_name = f"{vendor.name}_{int(vendor.id)}"
    folder = await graph.create_folder(folder_name)
    if not folder or not folder.get("id"):
        await session.rollback()
        return business_error("鍒涘缓渚涘簲鍟嗘枃浠跺す澶辫触")

    vendor.folder_id = folder.get("id") or None
    vendor.folder_url = folder.get("url") or None
    await session.flush()
    return success(RkVendorOut(id=int(vendor.id), name=vendor.name, code=vendor.code))


@router.post("/update")
async def update_vendor(
    payload: RkVendorUpdateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    result = await session.execute(select(RkVendor).where(RkVendor.id == payload.id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        return business_error("供应商不存在")

    old_name = vendor.name
    if payload.name is not None:
        vendor.name = payload.name
    if payload.code is not None:
        vendor.code = payload.code

    if vendor.folder_id and vendor.name != old_name:
        folder_name = f"{vendor.name}_{int(vendor.id)}"
        vendor.folder_url = await graph.change_folder_name(vendor.folder_id, folder_name) or vendor.folder_url

    if not vendor.folder_id:
        folder_name = f"{vendor.name}_{int(vendor.id)}"
        folder = await graph.create_folder(folder_name)
        if not folder or not folder.get("id"):
            await session.rollback()
            return business_error("鍒涘缓渚涘簲鍟嗘枃浠跺す澶辫触")
        vendor.folder_id = folder.get("id") or None
        vendor.folder_url = folder.get("url") or None

    vendor.updated_by = int(current.user.id)
    await session.flush()
    return success(RkVendorOut(id=int(vendor.id), name=vendor.name, code=vendor.code))

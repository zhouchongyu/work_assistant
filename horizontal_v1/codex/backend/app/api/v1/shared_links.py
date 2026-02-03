from __future__ import annotations

import mimetypes
import os
import tempfile
import uuid
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

import anyio
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.db.deps import get_db_session
from backend.app.integrations.redis_client import get_redis
from backend.app.integrations.sharepoint_graph.client import GraphClient, get_graph_client
from backend.app.models.rk_demand import RkDemand
from backend.app.models.rk_shared_links import RkSharedLinks
from backend.app.models.rk_supply import RkSupply
from backend.app.schemas.shared_links import (
    DownloadInfo,
    SharedLinksCreateRequest,
    SharedLinksCreateResult,
    SharedLinksGetTmpUrlRequest,
    SharedLinksGetTmpUrlResult,
    SharedLinksListRequest,
)

OFFICE_VIEWER_URL = "https://view.officeapps.live.com/op/view.aspx?src="

router = APIRouter(prefix="/shared_links", tags=["shared_links"])


def _public_base_url() -> str:
    return (os.environ.get("WA_PUBLIC_BASE_URL") or "").rstrip("/")


def _build_absolute_url(relative_path: str) -> str:
    base = _public_base_url()
    if not base:
        return relative_path
    return f"{base}{relative_path}"


def _parse_code(code: str) -> tuple[str, int] | None:
    if "-" not in code:
        return None
    token, num = code.rsplit("-", 1)
    try:
        return token, int(num)
    except ValueError:
        return None


async def _stream_supply_file(supply: RkSupply, *, graph: GraphClient) -> StreamingResponse:
    filename = supply.file_name or supply.name
    if supply.file_id:
        item = await graph.get_drive_item(str(supply.file_id))
        stream = await graph.stream_file_content(str(supply.file_id))
        media_type = item.content_type or (mimetypes.guess_type(filename or "")[0] or "application/octet-stream")
    elif supply.path:
        item = await graph.get_drive_item_from_share_url(str(supply.path))
        stream = await graph.stream_file_content_from_share_url(str(supply.path))
        media_type = item.content_type or (mimetypes.guess_type(filename or "")[0] or "application/octet-stream")
    else:
        return StreamingResponse(iter([b""]), status_code=404)

    headers = {}
    if filename:
        headers["Content-Disposition"] = f"inline; filename*=UTF-8''{quote_plus(filename)}"
    return StreamingResponse(stream, media_type=media_type, headers=headers)


@router.post("/create")
async def create_shared_links(
    payload: SharedLinksCreateRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not payload.ids:
        return business_error("ids不能为空")

    share_token = uuid.uuid4().hex
    minutes = int(payload.expire_minutes or 0)
    expire_at = datetime.now(timezone.utc) + (timedelta(minutes=minutes) if minutes > 0 else timedelta(days=7))

    record = RkSharedLinks(
        resource_type=payload.type,
        resource_id=[int(i) for i in payload.ids],
        share_token=share_token,
        expire_at=expire_at,
        created_by=int(current.user.id),
        updated_by=int(current.user.id),
        owner_id=int(current.user.id),
        department_id=current.user.department_id,
        active=True,
        to_be_confirmed=False,
    )
    session.add(record)
    await session.flush()

    return success(SharedLinksCreateResult(share_token=share_token))


@router.post("/shared_links_list")
async def shared_links_list(
    payload: SharedLinksListRequest,
    session: AsyncSession = Depends(get_db_session),
):
    now = datetime.now(timezone.utc)
    record = (
        await session.execute(
            select(RkSharedLinks).where(
                RkSharedLinks.share_token == payload.share_token,
                RkSharedLinks.resource_type == payload.type,
                RkSharedLinks.expire_at > now,
                RkSharedLinks.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not record or not record.resource_id:
        return success([])

    ids = [int(i) for i in record.resource_id if i is not None]
    if not ids:
        return success([])

    if payload.type == "demand":
        rows = (
            await session.execute(select(RkDemand).where(RkDemand.id.in_(ids)).order_by(RkDemand.id.desc()))
        ).scalars().all()
        return success([{"id": int(r.id), "remark": r.remark} for r in rows])

    if payload.type == "supply":
        rows = (
            await session.execute(select(RkSupply).where(RkSupply.id.in_(ids)).order_by(RkSupply.id.desc()))
        ).scalars().all()
        result = []
        for r in rows:
            raw_url = f"/api/v1/shared_links/resume_preview/{payload.share_token}-{int(r.id)}"
            download_url = raw_url
            url = raw_url
            filename = r.file_name or r.name
            if filename and not filename.lower().endswith(".pdf"):
                url = f"{OFFICE_VIEWER_URL}{quote_plus(_build_absolute_url(raw_url))}"
            result.append(
                {
                    "id": int(r.id),
                    "name": r.name,
                    "path": r.path,
                    "url": url,
                    "download_url": download_url,
                }
            )
        return success(result)

    return success([])


@router.get("/resume_preview/{code}")
async def resume_preview(
    code: str,
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    parsed = _parse_code(code)
    if not parsed:
        return business_error("code格式错误")
    share_token, supply_id = parsed

    now = datetime.now(timezone.utc)
    record = (
        await session.execute(
            select(RkSharedLinks).where(
                RkSharedLinks.share_token == share_token,
                RkSharedLinks.resource_type == "supply",
                RkSharedLinks.expire_at > now,
                RkSharedLinks.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not record or not record.resource_id or int(supply_id) not in [int(i) for i in record.resource_id]:
        return business_error("链接不存在或已过期")

    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("文件不存在")

    return await _stream_supply_file(supply, graph=graph)


@router.post("/download_all")
async def download_all(
    payload: DownloadInfo,
    session: AsyncSession = Depends(get_db_session),
    graph: GraphClient = Depends(get_graph_client),
):
    now = datetime.now(timezone.utc)
    record = (
        await session.execute(
            select(RkSharedLinks).where(
                RkSharedLinks.share_token == payload.share_token,
                RkSharedLinks.resource_type == "supply",
                RkSharedLinks.expire_at > now,
                RkSharedLinks.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not record or not record.resource_id:
        return business_error("链接不存在或已过期")

    allowed_ids = {int(i) for i in record.resource_id if i is not None}
    pick_ids = [int(i) for i in payload.ids if int(i) in allowed_ids]
    if not pick_ids:
        return business_error("没有可下载的文件")

    supplies = (
        await session.execute(select(RkSupply).where(RkSupply.id.in_(pick_ids)))
    ).scalars().all()
    files: list[tuple[str, str]] = []
    for s in supplies:
        if not s.file_id:
            continue
        files.append((s.file_name or s.name, str(s.file_id)))
    if not files:
        return business_error("没有可下载的文件")

    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp_dir.name) / f"supply-{payload.share_token}-all.zip"

    async def _download_one(file_id: str, dest: Path):
        stream = await graph.stream_file_content(file_id)
        async with await anyio.open_file(dest, "wb") as f:
            async for chunk in stream:
                await f.write(chunk)

    local_files: list[tuple[str, Path]] = []
    for name, file_id in files:
        safe_name = (name or file_id).replace("/", "_").replace("\\", "_")
        dest = Path(tmp_dir.name) / safe_name
        await _download_one(file_id, dest)
        local_files.append((safe_name, dest))

    def _build_zip():
        with zipfile.ZipFile(tmp_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for name, path in local_files:
                zf.write(path, arcname=name or path.name)

    await anyio.to_thread.run_sync(_build_zip)

    async def _iter_zip():
        async with await anyio.open_file(tmp_path, "rb") as f:
            while True:
                chunk = await f.read(1024 * 256)
                if not chunk:
                    break
                yield chunk

    headers = {"Content-Disposition": f'attachment; filename="supply-{payload.share_token}-all.zip"'}
    return StreamingResponse(
        _iter_zip(),
        media_type="application/zip",
        headers=headers,
        background=BackgroundTask(lambda: tmp_dir.cleanup()),
    )


@router.post("/get_tmp_url")
async def get_tmp_url(
    payload: SharedLinksGetTmpUrlRequest,
    current: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    _ = current
    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == payload.supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("简历不存在")

    file_name = supply.file_name or supply.name
    suffix = (Path(file_name).suffix or "").lstrip(".")
    code = uuid.uuid4().hex
    await redis.set(f"resume_preview:{code}", str(int(supply.id)), ex=5 * 60)

    rel = f"/api/v1/shared_links/resume_tmp_preview/{code}"
    if suffix.lower() == "pdf":
        path = rel
    else:
        path = f"{OFFICE_VIEWER_URL}{quote_plus(_build_absolute_url(rel))}"

    return success(SharedLinksGetTmpUrlResult(code=code, file_type=suffix or "bin", path=path))


@router.get("/resume_tmp_preview/{code}")
async def resume_tmp_preview(
    code: str,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
    graph: GraphClient = Depends(get_graph_client),
):
    supply_id_raw = await redis.get(f"resume_preview:{code}")
    if not supply_id_raw:
        return business_error("链接已经过期")
    try:
        supply_id = int(supply_id_raw)
    except ValueError:
        return business_error("链接已经过期")

    supply = (
        await session.execute(select(RkSupply).where(RkSupply.id == supply_id))
    ).scalar_one_or_none()
    if not supply:
        return business_error("文件不存在")

    return await _stream_supply_file(supply, graph=graph)

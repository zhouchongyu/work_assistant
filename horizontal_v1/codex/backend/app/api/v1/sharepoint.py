from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.integrations.sharepoint_graph.client import GraphClient, get_graph_client
from backend.app.schemas.sharepoint import (
    ChangeFolderNameRequest,
    ChangeFolderNameResult,
    MoveFileRequest,
    SharePointCreateFolderRequest,
    SharePointCreateFolderResult,
    SharePointGetFilesByFolderIdRequest,
    SharePointGetFilesRequest,
    SharePointGetFilesResult,
)

router = APIRouter(prefix="/sharepoint", tags=["sharepoint"])


@router.post("/create_folder")
async def create_folder(
    payload: SharePointCreateFolderRequest,
    current: CurrentUser = Depends(get_current_user),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    res = await graph.create_folder(payload.folder_name)
    if not res or not res.get("id"):
        return business_error("鍒涘缓鏂囦欢澶瑰け璐?")
    return success(SharePointCreateFolderResult(folder_url=res.get("url") or "", folder_id=res.get("id") or ""))


@router.get("/get_files")
async def get_files(
    request: SharePointGetFilesRequest = Depends(),
    current: CurrentUser = Depends(get_current_user),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    files, delta_link = await graph.get_files(request.folder_name, request.delta_link or "")
    return success(SharePointGetFilesResult(files=files, delta_link=delta_link))


@router.get("/get_files_by_folder_id")
async def get_files_by_folder_id(
    request: SharePointGetFilesByFolderIdRequest = Depends(),
    current: CurrentUser = Depends(get_current_user),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    files, delta_link = await graph.get_files_by_folder_id(request.folder_id, request.delta_link or "")
    return success(SharePointGetFilesResult(files=files, delta_link=delta_link))


@router.post("/change_folder_name")
async def change_folder_name(
    payload: ChangeFolderNameRequest,
    current: CurrentUser = Depends(get_current_user),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    web_url = await graph.change_folder_name(payload.folder_id, payload.new_name)
    return success(ChangeFolderNameResult(folder_url=web_url))


@router.post("/move_file")
async def move_file(
    payload: MoveFileRequest,
    current: CurrentUser = Depends(get_current_user),
    graph: GraphClient = Depends(get_graph_client),
):
    _ = current
    await graph.move_file(payload.file_id, payload.new_folder_id)
    return success(None)


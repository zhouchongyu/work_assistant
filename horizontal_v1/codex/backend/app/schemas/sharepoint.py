from __future__ import annotations

from backend.app.schemas.base import Schema


class SharePointCreateFolderRequest(Schema):
    folder_name: str


class SharePointCreateFolderResult(Schema):
    folder_url: str
    folder_id: str


class SharePointGetFilesRequest(Schema):
    folder_name: str
    delta_link: str | None = ""


class SharePointGetFilesByFolderIdRequest(Schema):
    folder_id: str
    delta_link: str | None = ""


class ChangeFolderNameRequest(Schema):
    folder_id: str
    new_name: str


class MoveFileRequest(Schema):
    file_id: str
    new_folder_id: str


class SharePointGetFilesResult(Schema):
    files: list[dict]
    delta_link: str


class ChangeFolderNameResult(Schema):
    folder_url: str


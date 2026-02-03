from __future__ import annotations

from backend.app.schemas.base import Schema


class SharedLinksListRequest(Schema):
    share_token: str
    type: str


class SharedLinksCreateRequest(Schema):
    ids: list[int]
    type: str
    expire_minutes: int | None = None


class SharedLinksCreateResult(Schema):
    share_token: str


class SharedLinksGetTmpUrlRequest(Schema):
    supply_id: int


class SharedLinksGetTmpUrlResult(Schema):
    code: str
    file_type: str
    path: str


class DownloadInfo(Schema):
    share_token: str
    ids: list[int]


from __future__ import annotations

from datetime import datetime

from backend.app.schemas.base import Schema


class NoticePageRequest(Schema):
    page: int = 1
    size: int = 20
    is_read: bool | None = None


class NoticeMarkReadRequest(Schema):
    ids: list[int]


class NoticeOut(Schema):
    id: int
    content: str | None = None
    is_read: bool
    type: str | None = None
    model: str | None = None
    created_at: datetime


class Pagination(Schema):
    total: int
    page: int
    size: int


class NoticePageResult(Schema):
    list: list[NoticeOut]
    pagination: Pagination


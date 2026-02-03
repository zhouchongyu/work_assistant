from __future__ import annotations

from backend.app.schemas.base import Schema


class RkCustomerCreateRequest(Schema):
    name: str
    code: str | None = None


class RkCustomerUpdateRequest(Schema):
    id: int
    name: str | None = None
    code: str | None = None


class PageRequest(Schema):
    page: int = 1
    size: int = 20
    active_switch: bool = False


class RkCustomerOut(Schema):
    id: int
    name: str
    code: str | None = None


class Pagination(Schema):
    total: int
    page: int
    size: int


class PageResult(Schema):
    list: list[RkCustomerOut]
    pagination: Pagination

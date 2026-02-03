from __future__ import annotations

from typing import Any

from backend.app.schemas.base import Schema


class CustomerColumnInfoItem(Schema):
    prop: str
    checked: bool
    label: str | None = None
    order_num: int | None = None
    extra: dict[str, Any] | None = None


class CustomerColumnSetRequest(Schema):
    name: str
    info: list[dict[str, Any]]


class CustomerColumnDeleteRequest(Schema):
    name: str


class ActiveSwitchSetRequest(Schema):
    status: bool


class ActiveSwitchOut(Schema):
    status: bool


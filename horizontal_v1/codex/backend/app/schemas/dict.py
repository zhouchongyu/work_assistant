from __future__ import annotations

from backend.app.schemas.base import Schema


class DictDataRequest(Schema):
    types: list[str] = []


class DictInfoItem(Schema):
    id: int
    name: str
    type_id: int
    parent_id: int | None = None
    order_num: int = 0
    value: str | int | None = None
    label: str | None = None
    key: str | None = None
    field_name: str | None = None
    is_show: bool = True
    is_process: bool = True


class Pagination(Schema):
    total: int
    page: int
    size: int


class PageResult(Schema):
    list: list
    pagination: Pagination


class DictTypeCreateRequest(Schema):
    name: str
    key: str
    page: str | None = None


class DictTypeUpdateRequest(Schema):
    id: int
    name: str | None = None
    key: str | None = None
    page: str | None = None


class DictTypeIdRequest(Schema):
    id: int


class DictTypeDeleteRequest(Schema):
    ids: list[int]


class DictTypePageRequest(Schema):
    page: int = 1
    size: int = 20
    key_word: str | None = None
    key: str | None = None
    key_like: str | None = None


class DictTypeOut(Schema):
    id: int
    name: str
    key: str
    page: str | None = None


class DictInfoCreateRequest(Schema):
    type_id: int
    name: str
    value: str | None = None
    order_num: int = 0
    remark: str | None = None
    parent_id: int | None = None
    field_name: str | None = None
    is_show: bool = True
    is_process: bool = True


class DictInfoUpdateRequest(Schema):
    id: int
    name: str | None = None
    value: str | None = None
    order_num: int | None = None
    remark: str | None = None
    parent_id: int | None = None
    field_name: str | None = None
    is_show: bool | None = None
    is_process: bool | None = None


class DictInfoIdRequest(Schema):
    id: int


class DictInfoDeleteRequest(Schema):
    ids: list[int]


class DictInfoPageRequest(Schema):
    page: int = 1
    size: int = 20
    key_word: str | None = None
    type_id: int | None = None


class DictInfoOut(Schema):
    id: int
    type_id: int
    name: str
    value: str | None = None
    order_num: int = 0
    remark: str | None = None
    parent_id: int | None = None
    field_name: str | None = None
    is_show: bool = True
    is_process: bool = True

from __future__ import annotations

from pydantic import Field

from backend.app.schemas.base import Schema


class EmptyRequest(Schema):
    pass


class DeptCreateRequest(Schema):
    name: str
    parent_id: int | None = None
    order_num: int = 0


class DeptOut(Schema):
    id: int
    name: str
    parent_id: int | None = None
    order_num: int = 0
    parent_name: str | None = None


class DeptTreeNode(Schema):
    id: int
    name: str
    parent_id: int | None = None
    order_num: int = 0
    children: list["DeptTreeNode"] = Field(default_factory=list)


DeptTreeNode.model_rebuild()


class DeptOrderItem(Schema):
    id: int
    parent_id: int | None = None
    order_num: int = 0


class PageRequest(Schema):
    page: int = 1
    size: int = 20
    key_word: str | None = None


class Pagination(Schema):
    total: int
    page: int
    size: int


class PageResult(Schema):
    list: list
    pagination: Pagination


class RoleCreateRequest(Schema):
    name: str
    label: str
    remark: str | None = None
    relevance: bool = False


class RoleOut(Schema):
    id: int
    name: str
    label: str | None = None
    remark: str | None = None
    relevance: bool = False


class UserCreateRequest(Schema):
    username: str
    password: str
    name: str | None = None
    nick_name: str | None = None
    head_img: str | None = None
    phone: str | None = None
    email: str | None = None
    remark: str | None = None
    status: int = 1
    department_id: int | None = None
    role_id_list: list[int] = Field(default_factory=list)


class UserUpdateRequest(Schema):
    id: int
    password: str | None = None
    name: str | None = None
    nick_name: str | None = None
    head_img: str | None = None
    phone: str | None = None
    email: str | None = None
    remark: str | None = None
    status: int | None = None
    department_id: int | None = None
    role_id_list: list[int] | None = None


class UserDisableRequest(Schema):
    id: int
    status: int


class UserMoveRequest(Schema):
    department_id: int
    user_ids: list[int]


class UserPageRequest(Schema):
    page: int = 1
    size: int = 20
    key_word: str | None = None
    status: int | None = None
    department_ids: list[int] = Field(default_factory=list)


class UserOut(Schema):
    id: int
    username: str
    name: str | None = None
    nick_name: str | None = None
    head_img: str | None = None
    phone: str | None = None
    email: str | None = None
    remark: str | None = None
    status: int
    department_id: int | None = None
    department_name: str | None = None
    role_name: str | None = None

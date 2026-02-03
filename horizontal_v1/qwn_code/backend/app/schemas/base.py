from app.schemas.response import BaseSchema
from typing import Optional, List
from datetime import datetime


class SysParamCreateRequest(BaseSchema):
    """系统参数创建请求"""
    key_name: str
    name: str
    value: str
    data_type: str = "string"  # string, number, boolean, json
    description: Optional[str] = None


class SysParamUpdateRequest(BaseSchema):
    """系统参数更新请求"""
    key_name: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None


class SysParamResponse(BaseSchema):
    """系统参数响应"""
    id: int
    key_name: str
    name: str
    value: str
    data_type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SysParamListResponse(BaseSchema):
    """系统参数列表响应"""
    items: List[SysParamResponse]
    total: int


class MenuCreateRequest(BaseSchema):
    """菜单创建请求"""
    name: str
    parent_id: Optional[int] = None
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    sort: int = 0
    hidden: bool = False
    description: Optional[str] = None


class MenuUpdateRequest(BaseSchema):
    """菜单更新请求"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    sort: Optional[int] = None
    hidden: Optional[bool] = None
    description: Optional[str] = None


class MenuResponse(BaseSchema):
    """菜单响应"""
    id: int
    name: str
    parent_id: Optional[int] = None
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    sort: int
    hidden: bool
    description: Optional[str] = None
    children: Optional[List['MenuResponse']] = []
    created_at: datetime
    updated_at: datetime


class MenuTreeResponse(BaseSchema):
    """菜单树响应"""
    items: List[MenuResponse]


class DepartmentCreateRequest(BaseSchema):
    """部门创建请求"""
    name: str
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class DepartmentUpdateRequest(BaseSchema):
    """部门更新请求"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(BaseSchema):
    """部门响应"""
    id: int
    name: str
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RoleCreateRequest(BaseSchema):
    """角色创建请求"""
    name: str
    code: str
    description: Optional[str] = None
    menu_ids: Optional[List[int]] = []


class RoleUpdateRequest(BaseSchema):
    """角色更新请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    menu_ids: Optional[List[int]] = None


class RoleResponse(BaseSchema):
    """角色响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    menu_ids: List[int] = []
    created_at: datetime
    updated_at: datetime
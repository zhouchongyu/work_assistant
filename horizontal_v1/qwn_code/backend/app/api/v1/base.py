from fastapi import APIRouter, Depends
from typing import List
from app.schemas.base import (
    SysParamCreateRequest, SysParamUpdateRequest, SysParamResponse,
    MenuCreateRequest, MenuUpdateRequest, MenuResponse, MenuTreeResponse,
    DepartmentCreateRequest, DepartmentUpdateRequest, DepartmentResponse,
    RoleCreateRequest, RoleUpdateRequest, RoleResponse
)
from app.services.base_service import SysParamService, MenuService, DepartmentService, RoleService
from app.api.v1.auth import get_current_user
from app.core.exceptions import BusinessError


router = APIRouter()


# 系统参数相关接口
@router.post("/sys/param", response_model=SysParamResponse)
async def create_sys_param(
    request: SysParamCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建系统参数"""
    # 检查是否有权限
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限创建系统参数", code=10033)
    
    param_data = request.model_dump()
    return await SysParamService.create_param(param_data)


@router.get("/sys/param/{param_id}", response_model=SysParamResponse)
async def get_sys_param(
    param_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取系统参数"""
    param = await SysParamService.get_param_by_id(param_id)
    if not param:
        raise BusinessError(message="参数不存在", code=10034)
    return param


@router.put("/sys/param/{param_id}", response_model=SysParamResponse)
async def update_sys_param(
    param_id: int,
    request: SysParamUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新系统参数"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限更新系统参数", code=10033)
    
    update_data = request.model_dump(exclude_unset=True)
    result = await SysParamService.update_param(param_id, update_data)
    if not result:
        raise BusinessError(message="参数不存在", code=10034)
    return result


@router.delete("/sys/param/{param_id}")
async def delete_sys_param(
    param_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除系统参数"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限删除系统参数", code=10033)
    
    success = await SysParamService.delete_param(param_id)
    if not success:
        raise BusinessError(message="参数不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


@router.get("/sys/param/key/{key_name}", response_model=SysParamResponse)
async def get_sys_param_by_key(key_name: str):
    """根据键名获取系统参数（公开接口）"""
    param = await SysParamService.get_param_by_key(key_name)
    if not param:
        raise BusinessError(message="参数不存在", code=10034)
    return param


# 菜单相关接口
@router.post("/sys/menu", response_model=MenuResponse)
async def create_menu(
    request: MenuCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建菜单"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限创建菜单", code=10033)
    
    menu_data = request.model_dump()
    return await MenuService.create_menu(menu_data)


@router.get("/sys/menu/tree", response_model=MenuTreeResponse)
async def get_menu_tree(current_user: dict = Depends(get_current_user)):
    """获取菜单树"""
    menus = await MenuService.get_menu_tree()
    return MenuTreeResponse(items=menus)


@router.put("/sys/menu/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: int,
    request: MenuUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新菜单"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限更新菜单", code=10033)
    
    update_data = request.model_dump(exclude_unset=True)
    result = await MenuService.update_menu(menu_id, update_data)
    if not result:
        raise BusinessError(message="菜单不存在", code=10034)
    return result


@router.delete("/sys/menu/{menu_id}")
async def delete_menu(
    menu_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除菜单"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限删除菜单", code=10033)
    
    success = await MenuService.delete_menu(menu_id)
    if not success:
        raise BusinessError(message="菜单不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


# 部门相关接口
@router.post("/sys/department", response_model=DepartmentResponse)
async def create_department(
    request: DepartmentCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建部门"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限创建部门", code=10033)
    
    dept_data = request.model_dump()
    return await DepartmentService.create_department(dept_data)


@router.get("/sys/department/{dept_id}", response_model=DepartmentResponse)
async def get_department(dept_id: int):
    """获取部门"""
    dept = await DepartmentService.get_department_by_id(dept_id)
    if not dept:
        raise BusinessError(message="部门不存在", code=10034)
    return dept


@router.put("/sys/department/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: int,
    request: DepartmentUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新部门"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限更新部门", code=10033)
    
    update_data = request.model_dump(exclude_unset=True)
    result = await DepartmentService.update_department(dept_id, update_data)
    if not result:
        raise BusinessError(message="部门不存在", code=10034)
    return result


@router.delete("/sys/department/{dept_id}")
async def delete_department(
    dept_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除部门"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限删除部门", code=10033)
    
    success = await DepartmentService.delete_department(dept_id)
    if not success:
        raise BusinessError(message="部门不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


# 角色相关接口
@router.post("/sys/role", response_model=RoleResponse)
async def create_role(
    request: RoleCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建角色"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限创建角色", code=10033)
    
    role_data = request.model_dump()
    return await RoleService.create_role(role_data)


@router.get("/sys/role/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int):
    """获取角色"""
    role = await RoleService.get_role_by_id(role_id)
    if not role:
        raise BusinessError(message="角色不存在", code=10034)
    return role


@router.put("/sys/role/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    request: RoleUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新角色"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限更新角色", code=10033)
    
    update_data = request.model_dump(exclude_unset=True)
    result = await RoleService.update_role(role_id, update_data)
    if not result:
        raise BusinessError(message="角色不存在", code=10034)
    return result


@router.delete("/sys/role/{role_id}")
async def delete_role(
    role_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除角色"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限删除角色", code=10033)
    
    success = await RoleService.delete_role(role_id)
    if not success:
        raise BusinessError(message="角色不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "base"}
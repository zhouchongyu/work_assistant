from app.db.dao.base_dao import SysParamDAO, MenuDAO, DepartmentDAO, RoleDAO
from app.db.session import get_db_session
from typing import Optional, List
from app.schemas.base import SysParamResponse, MenuResponse, DepartmentResponse, RoleResponse


class SysParamService:
    """系统参数服务"""
    
    @staticmethod
    async def get_param_by_key(key_name: str) -> Optional[SysParamResponse]:
        """根据键名获取参数"""
        async for db in get_db_session():
            param = await SysParamDAO.get_by_key(db, key_name)
            if param:
                return SysParamResponse(
                    id=param.id,
                    key_name=param.key_name,
                    name=param.name,
                    value=param.value,
                    data_type=param.data_type,
                    description=param.description,
                    created_at=param.created_at,
                    updated_at=param.updated_at
                )
            return None
    
    @staticmethod
    async def get_param_by_id(param_id: int) -> Optional[SysParamResponse]:
        """根据ID获取参数"""
        async for db in get_db_session():
            param = await SysParamDAO.get_by_id(db, param_id)
            if param:
                return SysParamResponse(
                    id=param.id,
                    key_name=param.key_name,
                    name=param.name,
                    value=param.value,
                    data_type=param.data_type,
                    description=param.description,
                    created_at=param.created_at,
                    updated_at=param.updated_at
                )
            return None
    
    @staticmethod
    async def get_all_params() -> List[SysParamResponse]:
        """获取所有参数"""
        async for db in get_db_session():
            params = await SysParamDAO.get_all(db)
            return [
                SysParamResponse(
                    id=param.id,
                    key_name=param.key_name,
                    name=param.name,
                    value=param.value,
                    data_type=param.data_type,
                    description=param.description,
                    created_at=param.created_at,
                    updated_at=param.updated_at
                )
                for param in params
            ]
    
    @staticmethod
    async def create_param(param_data: dict) -> SysParamResponse:
        """创建参数"""
        async for db in get_db_session():
            param = await SysParamDAO.create(db, param_data)
            return SysParamResponse(
                id=param.id,
                key_name=param.key_name,
                name=param.name,
                value=param.value,
                data_type=param.data_type,
                description=param.description,
                created_at=param.created_at,
                updated_at=param.updated_at
            )
    
    @staticmethod
    async def update_param(param_id: int, update_data: dict) -> Optional[SysParamResponse]:
        """更新参数"""
        async for db in get_db_session():
            param = await SysParamDAO.update(db, param_id, update_data)
            if param:
                return SysParamResponse(
                    id=param.id,
                    key_name=param.key_name,
                    name=param.name,
                    value=param.value,
                    data_type=param.data_type,
                    description=param.description,
                    created_at=param.created_at,
                    updated_at=param.updated_at
                )
            return None
    
    @staticmethod
    async def delete_param(param_id: int) -> bool:
        """删除参数"""
        async for db in get_db_session():
            return await SysParamDAO.delete(db, param_id)


class MenuService:
    """菜单服务"""
    
    @staticmethod
    async def get_menu_by_id(menu_id: int) -> Optional[MenuResponse]:
        """根据ID获取菜单"""
        async for db in get_db_session():
            menu = await MenuDAO.get_by_id(db, menu_id)
            if menu:
                return MenuResponse(
                    id=menu.id,
                    name=menu.name,
                    parent_id=menu.parent_id,
                    path=menu.path,
                    component=menu.component,
                    redirect=menu.redirect,
                    icon=menu.icon,
                    sort=menu.sort,
                    hidden=menu.hidden,
                    description=menu.description,
                    created_at=menu.created_at,
                    updated_at=menu.updated_at
                )
            return None
    
    @staticmethod
    async def get_menu_tree() -> List[MenuResponse]:
        """获取菜单树"""
        async for db in get_db_session():
            menus = await MenuDAO.get_menu_tree(db)
            return [
                MenuResponse(
                    id=menu.id,
                    name=menu.name,
                    parent_id=menu.parent_id,
                    path=menu.path,
                    component=menu.component,
                    redirect=menu.redirect,
                    icon=menu.icon,
                    sort=menu.sort,
                    hidden=menu.hidden,
                    description=menu.description,
                    children=[
                        MenuResponse(
                            id=child.id,
                            name=child.name,
                            parent_id=child.parent_id,
                            path=child.path,
                            component=child.component,
                            redirect=child.redirect,
                            icon=child.icon,
                            sort=child.sort,
                            hidden=child.hidden,
                            description=child.description,
                            created_at=child.created_at,
                            updated_at=child.updated_at
                        )
                        for child in menu.children or []
                    ] if menu.children else [],
                    created_at=menu.created_at,
                    updated_at=menu.updated_at
                )
                for menu in menus
            ]
    
    @staticmethod
    async def create_menu(menu_data: dict) -> MenuResponse:
        """创建菜单"""
        async for db in get_db_session():
            menu = await MenuDAO.create(db, menu_data)
            return MenuResponse(
                id=menu.id,
                name=menu.name,
                parent_id=menu.parent_id,
                path=menu.path,
                component=menu.component,
                redirect=menu.redirect,
                icon=menu.icon,
                sort=menu.sort,
                hidden=menu.hidden,
                description=menu.description,
                created_at=menu.created_at,
                updated_at=menu.updated_at
            )
    
    @staticmethod
    async def update_menu(menu_id: int, update_data: dict) -> Optional[MenuResponse]:
        """更新菜单"""
        async for db in get_db_session():
            menu = await MenuDAO.update(db, menu_id, update_data)
            if menu:
                return MenuResponse(
                    id=menu.id,
                    name=menu.name,
                    parent_id=menu.parent_id,
                    path=menu.path,
                    component=menu.component,
                    redirect=menu.redirect,
                    icon=menu.icon,
                    sort=menu.sort,
                    hidden=menu.hidden,
                    description=menu.description,
                    created_at=menu.created_at,
                    updated_at=menu.updated_at
                )
            return None
    
    @staticmethod
    async def delete_menu(menu_id: int) -> bool:
        """删除菜单"""
        async for db in get_db_session():
            return await MenuDAO.delete(db, menu_id)


class DepartmentService:
    """部门服务"""
    
    @staticmethod
    async def get_department_by_id(dept_id: int) -> Optional[DepartmentResponse]:
        """根据ID获取部门"""
        async for db in get_db_session():
            dept = await DepartmentDAO.get_by_id(db, dept_id)
            if dept:
                return DepartmentResponse(
                    id=dept.id,
                    name=dept.name,
                    parent_id=dept.parent_id,
                    leader_id=dept.leader_id,
                    phone=dept.phone,
                    email=dept.email,
                    description=dept.description,
                    created_at=dept.created_at,
                    updated_at=dept.updated_at
                )
            return None
    
    @staticmethod
    async def create_department(dept_data: dict) -> DepartmentResponse:
        """创建部门"""
        async for db in get_db_session():
            dept = await DepartmentDAO.create(db, dept_data)
            return DepartmentResponse(
                id=dept.id,
                name=dept.name,
                parent_id=dept.parent_id,
                leader_id=dept.leader_id,
                phone=dept.phone,
                email=dept.email,
                description=dept.description,
                created_at=dept.created_at,
                updated_at=dept.updated_at
            )
    
    @staticmethod
    async def update_department(dept_id: int, update_data: dict) -> Optional[DepartmentResponse]:
        """更新部门"""
        async for db in get_db_session():
            dept = await DepartmentDAO.update(db, dept_id, update_data)
            if dept:
                return DepartmentResponse(
                    id=dept.id,
                    name=dept.name,
                    parent_id=dept.parent_id,
                    leader_id=dept.leader_id,
                    phone=dept.phone,
                    email=dept.email,
                    description=dept.description,
                    created_at=dept.created_at,
                    updated_at=dept.updated_at
                )
            return None
    
    @staticmethod
    async def delete_department(dept_id: int) -> bool:
        """删除部门"""
        async for db in get_db_session():
            return await DepartmentDAO.delete(db, dept_id)


class RoleService:
    """角色服务"""
    
    @staticmethod
    async def get_role_by_id(role_id: int) -> Optional[RoleResponse]:
        """根据ID获取角色"""
        async for db in get_db_session():
            role = await RoleDAO.get_by_id(db, role_id)
            if role:
                return RoleResponse(
                    id=role.id,
                    name=role.name,
                    code=role.code,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at
                )
            return None
    
    @staticmethod
    async def get_role_by_code(code: str) -> Optional[RoleResponse]:
        """根据编码获取角色"""
        async for db in get_db_session():
            role = await RoleDAO.get_by_code(db, code)
            if role:
                return RoleResponse(
                    id=role.id,
                    name=role.name,
                    code=role.code,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at
                )
            return None
    
    @staticmethod
    async def create_role(role_data: dict) -> RoleResponse:
        """创建角色"""
        async for db in get_db_session():
            role = await RoleDAO.create(db, role_data)
            return RoleResponse(
                id=role.id,
                name=role.name,
                code=role.code,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at
            )
    
    @staticmethod
    async def update_role(role_id: int, update_data: dict) -> Optional[RoleResponse]:
        """更新角色"""
        async for db in get_db_session():
            role = await RoleDAO.update(db, role_id, update_data)
            if role:
                return RoleResponse(
                    id=role.id,
                    name=role.name,
                    code=role.code,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at
                )
            return None
    
    @staticmethod
    async def delete_role(role_id: int) -> bool:
        """删除角色"""
        async for db in get_db_session():
            return await RoleDAO.delete(db, role_id)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.base_models import SysParam, Menu, Department, Role
from typing import Optional, List


class SysParamDAO:
    """系统参数数据访问对象"""
    
    @staticmethod
    async def get_by_key(db: AsyncSession, key_name: str) -> Optional[SysParam]:
        """根据键名获取参数"""
        stmt = select(SysParam).where(SysParam.key_name == key_name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, param_id: int) -> Optional[SysParam]:
        """根据ID获取参数"""
        stmt = select(SysParam).where(SysParam.id == param_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[SysParam]:
        """获取所有参数"""
        stmt = select(SysParam)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, param_data: dict) -> SysParam:
        """创建参数"""
        db_param = SysParam(**param_data)
        db.add(db_param)
        await db.commit()
        await db.refresh(db_param)
        return db_param
    
    @staticmethod
    async def update(db: AsyncSession, param_id: int, update_data: dict) -> SysParam:
        """更新参数"""
        db_param = await SysParamDAO.get_by_id(db, param_id)
        if not db_param:
            return None
        
        for key, value in update_data.items():
            setattr(db_param, key, value)
        
        await db.commit()
        await db.refresh(db_param)
        return db_param
    
    @staticmethod
    async def delete(db: AsyncSession, param_id: int) -> bool:
        """删除参数"""
        db_param = await SysParamDAO.get_by_id(db, param_id)
        if not db_param:
            return False
        
        await db.delete(db_param)
        await db.commit()
        return True


class MenuDAO:
    """菜单数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        stmt = select(Menu).where(Menu.id == menu_id).options(selectinload(Menu.children))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Menu]:
        """获取所有菜单"""
        stmt = select(Menu).order_by(Menu.sort)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_parent_id(db: AsyncSession, parent_id: Optional[int]) -> List[Menu]:
        """根据父ID获取菜单"""
        stmt = select(Menu).where(Menu.parent_id == parent_id).order_by(Menu.sort)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_menu_tree(db: AsyncSession) -> List[Menu]:
        """获取菜单树"""
        # 获取所有菜单
        all_menus = await MenuDAO.get_all(db)
        
        # 构建菜单树
        menu_dict = {menu.id: menu for menu in all_menus}
        root_menus = []
        
        for menu in all_menus:
            if menu.parent_id is None:
                root_menus.append(menu)
            else:
                parent = menu_dict.get(menu.parent_id)
                if parent:
                    if parent.children is None:
                        parent.children = []
                    parent.children.append(menu)
        
        return root_menus
    
    @staticmethod
    async def create(db: AsyncSession, menu_data: dict) -> Menu:
        """创建菜单"""
        db_menu = Menu(**menu_data)
        db.add(db_menu)
        await db.commit()
        await db.refresh(db_menu)
        return db_menu
    
    @staticmethod
    async def update(db: AsyncSession, menu_id: int, update_data: dict) -> Menu:
        """更新菜单"""
        db_menu = await MenuDAO.get_by_id(db, menu_id)
        if not db_menu:
            return None
        
        for key, value in update_data.items():
            setattr(db_menu, key, value)
        
        await db.commit()
        await db.refresh(db_menu)
        return db_menu
    
    @staticmethod
    async def delete(db: AsyncSession, menu_id: int) -> bool:
        """删除菜单"""
        db_menu = await MenuDAO.get_by_id(db, menu_id)
        if not db_menu:
            return False
        
        await db.delete(db_menu)
        await db.commit()
        return True


class DepartmentDAO:
    """部门数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, dept_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        stmt = select(Department).where(Department.id == dept_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Department]:
        """获取所有部门"""
        stmt = select(Department)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, dept_data: dict) -> Department:
        """创建部门"""
        db_dept = Department(**dept_data)
        db.add(db_dept)
        await db.commit()
        await db.refresh(db_dept)
        return db_dept
    
    @staticmethod
    async def update(db: AsyncSession, dept_id: int, update_data: dict) -> Department:
        """更新部门"""
        db_dept = await DepartmentDAO.get_by_id(db, dept_id)
        if not db_dept:
            return None
        
        for key, value in update_data.items():
            setattr(db_dept, key, value)
        
        await db.commit()
        await db.refresh(db_dept)
        return db_dept
    
    @staticmethod
    async def delete(db: AsyncSession, dept_id: int) -> bool:
        """删除部门"""
        db_dept = await DepartmentDAO.get_by_id(db, dept_id)
        if not db_dept:
            return False
        
        await db.delete(db_dept)
        await db.commit()
        return True


class RoleDAO:
    """角色数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        stmt = select(Role).where(Role.id == role_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Role]:
        """根据编码获取角色"""
        stmt = select(Role).where(Role.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Role]:
        """获取所有角色"""
        stmt = select(Role)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, role_data: dict) -> Role:
        """创建角色"""
        db_role = Role(**role_data)
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        return db_role
    
    @staticmethod
    async def update(db: AsyncSession, role_id: int, update_data: dict) -> Role:
        """更新角色"""
        db_role = await RoleDAO.get_by_id(db, role_id)
        if not db_role:
            return None
        
        for key, value in update_data.items():
            setattr(db_role, key, value)
        
        await db.commit()
        await db.refresh(db_role)
        return db_role
    
    @staticmethod
    async def delete(db: AsyncSession, role_id: int) -> bool:
        """删除角色"""
        db_role = await RoleDAO.get_by_id(db, role_id)
        if not db_role:
            return False
        
        await db.delete(db_role)
        await db.commit()
        return True
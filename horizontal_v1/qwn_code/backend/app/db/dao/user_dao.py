from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.services.auth import get_password_hash
from typing import Optional


class UserDao:
    """用户数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        stmt = select(User).where(User.phone == phone)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> User:
        """创建用户"""
        # 对密码进行哈希处理
        if 'password' in user_data:
            user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: dict) -> User:
        """更新用户"""
        db_user = await UserDao.get_by_id(db, user_id)
        if not db_user:
            return None
        
        # 如果有密码更新，需要哈希处理
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """删除用户"""
        db_user = await UserDao.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
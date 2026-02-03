from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.task import TaskInfo, TaskLog
from typing import Optional, List


class TaskInfoDAO:
    """任务信息数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int) -> Optional[TaskInfo]:
        """根据ID获取任务"""
        stmt = select(TaskInfo).where(TaskInfo.id == task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[TaskInfo]:
        """获取所有任务"""
        stmt = select(TaskInfo)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, task_data: dict) -> TaskInfo:
        """创建任务"""
        db_task = TaskInfo(**task_data)
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def update(db: AsyncSession, task_id: int, update_data: dict) -> TaskInfo:
        """更新任务"""
        db_task = await TaskInfoDAO.get_by_id(db, task_id)
        if not db_task:
            return None
        
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def delete(db: AsyncSession, task_id: int) -> bool:
        """删除任务"""
        db_task = await TaskInfoDAO.get_by_id(db, task_id)
        if not db_task:
            return False
        
        await db.delete(db_task)
        await db.commit()
        return True


class TaskLogDAO:
    """任务日志数据访问对象"""
    
    @staticmethod
    async def get_by_task_id(db: AsyncSession, task_id: int, skip: int = 0, limit: int = 100) -> List[TaskLog]:
        """根据任务ID获取日志"""
        stmt = select(TaskLog).where(TaskLog.task_id == task_id).offset(skip).limit(limit).order_by(TaskLog.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, log_data: dict) -> TaskLog:
        """创建任务日志"""
        db_log = TaskLog(**log_data)
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        return db_log
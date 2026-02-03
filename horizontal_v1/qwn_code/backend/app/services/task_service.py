from typing import Optional, List
from app.db.dao.task_dao import TaskInfoDAO, TaskLogDAO
from app.db.session import get_db_session
from app.models.task import TaskInfo
from app.schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskLogResponse, TaskLogItem
from app.core.config.settings import settings
import asyncio


class TaskService:
    """任务服务类"""
    
    @staticmethod
    async def get_task_by_id(task_id: int) -> Optional[TaskResponse]:
        """根据ID获取任务"""
        async for db in get_db_session():
            task = await TaskInfoDAO.get_by_id(db, task_id)
            if task:
                return TaskResponse(
                    id=task.id,
                    name=task.name,
                    type=task.type,
                    cron_expression=task.cron_expression,
                    handler=task.handler,
                    description=task.description,
                    enabled=task.enabled,
                    status=task.status,
                    last_run_time=task.last_run_time,
                    next_run_time=task.next_run_time,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
            return None
    
    @staticmethod
    async def create_task(task_data: dict) -> TaskResponse:
        """创建任务"""
        async for db in get_db_session():
            task = await TaskInfoDAO.create(db, task_data)
            return TaskResponse(
                id=task.id,
                name=task.name,
                type=task.type,
                cron_expression=task.cron_expression,
                handler=task.handler,
                description=task.description,
                enabled=task.enabled,
                status=task.status,
                last_run_time=task.last_run_time,
                next_run_time=task.next_run_time,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
    
    @staticmethod
    async def update_task(task_id: int, update_data: dict) -> Optional[TaskResponse]:
        """更新任务"""
        async for db in get_db_session():
            task = await TaskInfoDAO.update(db, task_id, update_data)
            if task:
                return TaskResponse(
                    id=task.id,
                    name=task.name,
                    type=task.type,
                    cron_expression=task.cron_expression,
                    handler=task.handler,
                    description=task.description,
                    enabled=task.enabled,
                    status=task.status,
                    last_run_time=task.last_run_time,
                    next_run_time=task.next_run_time,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
            return None
    
    @staticmethod
    async def delete_task(task_id: int) -> bool:
        """删除任务"""
        async for db in get_db_session():
            return await TaskInfoDAO.delete(db, task_id)
    
    @staticmethod
    async def get_task_logs(task_id: Optional[int], page: int = 1, size: int = 20) -> TaskLogResponse:
        """获取任务日志"""
        async for db in get_db_session():
            logs, total = await TaskLogDAO.get_paginated_logs(db, task_id, page, size)
            
            items = [
                TaskLogItem(
                    id=log.id,
                    task_id=log.task_id,
                    status=log.status,
                    message=log.message,
                    created_at=log.created_at
                )
                for log in logs
            ]
            
            return TaskLogResponse(
                items=items,
                total=total,
                page=page,
                size=size
            )
    
    @staticmethod
    async def execute_task_once(task_id: int) -> dict:
        """执行任务一次"""
        # 这里应该实现具体的任务执行逻辑
        # 为了演示，我们只是返回成功
        return {
            "success": True,
            "message": f"任务 {task_id} 已执行"
        }
    
    @staticmethod
    async def start_task(task_id: int) -> dict:
        """启动任务"""
        # 这里应该实现任务启动逻辑
        async for db in get_db_session():
            await TaskInfoDAO.update(db, task_id, {"enabled": True, "status": "RUNNING"})
            return {"success": True, "message": f"任务 {task_id} 已启动"}
    
    @staticmethod
    async def stop_task(task_id: int) -> dict:
        """停止任务"""
        # 这里应该实现任务停止逻辑
        async for db in get_db_session():
            await TaskInfoDAO.update(db, task_id, {"enabled": False, "status": "STOPPED"})
            return {"success": True, "message": f"任务 {task_id} 已停止"}
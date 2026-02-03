from fastapi import APIRouter, Depends
from typing import List
from app.schemas.task import (
    TaskCreateRequest, TaskUpdateRequest, TaskResponse, 
    TaskExecuteRequest, TaskExecuteResponse, 
    TaskControlRequest, TaskControlResponse, 
    TaskLogRequest, TaskLogResponse
)
from app.services.task_service import TaskService
from app.api.v1.auth import get_current_user
from app.core.exceptions import BusinessError


router = APIRouter()
task_service = TaskService()


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建任务"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限创建任务", code=10033)
    
    task_data = request.model_dump()
    return await TaskService.create_task(task_data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """获取任务"""
    task = await TaskService.get_task_by_id(task_id)
    if not task:
        raise BusinessError(message="任务不存在", code=10034)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新任务"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限更新任务", code=10033)
    
    update_data = request.model_dump(exclude_unset=True)
    result = await TaskService.update_task(task_id, update_data)
    if not result:
        raise BusinessError(message="任务不存在", code=10034)
    return result


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除任务"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限删除任务", code=10033)
    
    success = await TaskService.delete_task(task_id)
    if not success:
        raise BusinessError(message="任务不存在", code=10034)
    return {"code": 1000, "message": "删除成功"}


@router.get("/", response_model=List[TaskResponse])
async def get_tasks():
    """获取所有任务"""
    return await TaskService.get_all_tasks()


@router.post("/execute", response_model=TaskExecuteResponse)
async def execute_task_once(
    request: TaskExecuteRequest,
    current_user: dict = Depends(get_current_user)
):
    """执行任务一次"""
    return await TaskService.execute_task_once(request.task_id)


@router.post("/start", response_model=TaskControlResponse)
async def start_task(
    request: TaskControlRequest,
    current_user: dict = Depends(get_current_user)
):
    """启动任务"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限启动任务", code=10033)
    
    return await TaskService.start_task(request.task_id)


@router.post("/stop", response_model=TaskControlResponse)
async def stop_task(
    request: TaskControlRequest,
    current_user: dict = Depends(get_current_user)
):
    """暂停任务"""
    if not current_user.get("is_superuser", False):
        raise BusinessError(message="没有权限暂停任务", code=10033)
    
    return await TaskService.stop_task(request.task_id)


@router.post("/logs", response_model=TaskLogResponse)
async def get_task_logs(
    request: TaskLogRequest,
    current_user: dict = Depends(get_current_user)
):
    """获取任务日志"""
    return await TaskService.get_task_logs(
        task_id=request.task_id,
        page=request.page,
        size=request.size
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "task"}
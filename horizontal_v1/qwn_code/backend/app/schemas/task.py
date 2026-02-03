from app.schemas.response import BaseSchema
from typing import Optional, List
from datetime import datetime


class TaskCreateRequest(BaseSchema):
    """任务创建请求"""
    name: str
    type: int
    cron_expression: str
    handler: str
    description: Optional[str] = None
    enabled: bool = True


class TaskUpdateRequest(BaseSchema):
    """任务更新请求"""
    name: Optional[str] = None
    type: Optional[int] = None
    cron_expression: Optional[str] = None
    handler: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class TaskResponse(BaseSchema):
    """任务响应"""
    id: int
    name: str
    type: int
    cron_expression: str
    handler: str
    description: Optional[str] = None
    enabled: bool
    status: str
    last_run_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskExecuteRequest(BaseSchema):
    """任务执行请求"""
    task_id: int


class TaskExecuteResponse(BaseSchema):
    """任务执行响应"""
    success: bool
    message: str


class TaskControlRequest(BaseSchema):
    """任务控制请求"""
    task_id: int


class TaskControlResponse(BaseSchema):
    """任务控制响应"""
    success: bool
    message: str


class TaskLogRequest(BaseSchema):
    """任务日志请求"""
    task_id: Optional[int] = None
    page: int = 1
    size: int = 20


class TaskLogItem(BaseSchema):
    """任务日志项"""
    id: int
    task_id: int
    status: str
    message: str
    created_at: datetime


class TaskLogResponse(BaseSchema):
    """任务日志响应"""
    items: List[TaskLogItem]
    total: int
    page: int
    size: int
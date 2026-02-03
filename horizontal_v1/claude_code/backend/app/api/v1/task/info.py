"""
Task info API endpoints.

Provides:
- Task CRUD operations
- Task start/stop/run controls

Reference:
- cool-admin-midway/src/modules/task/controller/admin/info.ts
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.responses import success_response
from app.middleware.authority import get_current_user
from app.services.task import task_scheduler

logger = logging.getLogger("work_assistant.api.task")

router = APIRouter()


# ==================== Request Schemas ====================

class TaskCreateRequest(BaseModel):
    """Task creation request."""

    name: str = Field(..., min_length=1, max_length=100, description="Task name")
    cron: str | None = Field(None, description="Cron expression (for cron tasks)")
    every: int | None = Field(None, description="Interval in milliseconds (for interval tasks)")
    limit: int | None = Field(None, description="Max execution count (null for unlimited)")
    status: int = Field(1, description="Status: 0=stopped, 1=running")
    taskType: int = Field(0, description="Task type: 0=cron, 1=interval")
    type: int = Field(0, description="Type: 0=system, 1=user")
    service: str | None = Field(None, description="Service method to invoke")
    data: str | None = Field(None, description="Task data (JSON)")
    remark: str | None = Field(None, description="Remarks")
    startDate: datetime | None = Field(None, description="Start date")
    endDate: datetime | None = Field(None, description="End date")


class TaskUpdateRequest(TaskCreateRequest):
    """Task update request."""

    id: int = Field(..., description="Task ID")


class TaskPageRequest(BaseModel):
    """Task list pagination request."""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    status: int | None = Field(None, description="Filter by status")
    keyWord: str | None = Field(None, description="Search keyword")


# ==================== Endpoints ====================

@router.post("/info/page", summary="Get task list")
async def get_task_page(
    body: TaskPageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Get paginated task list."""
    result = await task_scheduler.list_tasks(
        page=body.page,
        size=body.size,
        status=body.status,
    )
    return success_response(data=result)


@router.post("/info/add", summary="Create task")
async def create_task(
    body: TaskCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new task."""
    task_data = body.model_dump(exclude_none=True)
    task = await task_scheduler.add_task(task_data)
    return success_response(data={"id": task.id})


@router.post("/info/update", summary="Update task")
async def update_task(
    body: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing task."""
    task_data = body.model_dump(exclude_none=True)
    task = await task_scheduler.add_task(task_data)
    return success_response(data={"id": task.id})


@router.post("/info/info", summary="Get task info")
async def get_task_info(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get task details by ID."""
    task = await task_scheduler.get_task(id)
    if not task:
        return success_response(data=None, message="Task not found")
    return success_response(data=task_scheduler._task_to_dict(task))


@router.post("/info/delete", summary="Delete task")
async def delete_task(
    ids: str | list[int],
    current_user: dict = Depends(get_current_user),
):
    """Delete one or more tasks."""
    if isinstance(ids, str):
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    else:
        id_list = ids

    for task_id in id_list:
        await task_scheduler.delete_task(task_id)

    return success_response(message="Tasks deleted")


@router.post("/info/start", summary="Start task")
async def start_task(
    id: int,
    type: int | None = None,
    current_user: dict = Depends(get_current_user),
):
    """Start a task."""
    result = await task_scheduler.start_task(id)
    if result:
        return success_response(message="Task started")
    return success_response(message="Failed to start task")


@router.post("/info/stop", summary="Stop task")
async def stop_task(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    """Stop a running task."""
    result = await task_scheduler.stop_task(id)
    if result:
        return success_response(message="Task stopped")
    return success_response(message="Task was not running")


@router.post("/info/once", summary="Run task once")
async def run_task_once(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    """Execute a task once immediately."""
    await task_scheduler.run_once(id)
    return success_response(message="Task executed")

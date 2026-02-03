"""
Task log API endpoints.

Provides:
- Task execution log queries

Reference:
- cool-admin-midway/src/modules/task/controller/admin/log.ts
"""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.responses import success_response
from app.middleware.authority import get_current_user
from app.services.task import task_scheduler

logger = logging.getLogger("work_assistant.api.task.log")

router = APIRouter()


# ==================== Request Schemas ====================

class LogPageRequest(BaseModel):
    """Task log pagination request."""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    id: int | None = Field(None, description="Filter by task ID")
    status: int | None = Field(None, description="Filter by status")


# ==================== Endpoints ====================

@router.post("/log/page", summary="Get task logs")
async def get_task_logs(
    body: LogPageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Get paginated task execution logs."""
    result = await task_scheduler.get_task_logs(
        task_id=body.id,
        status=body.status,
        page=body.page,
        size=body.size,
    )
    return success_response(data=result)

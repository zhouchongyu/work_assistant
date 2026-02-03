"""
Task scheduling API module.

Provides task management endpoints.
"""

from fastapi import APIRouter

from app.api.v1.task.info import router as info_router
from app.api.v1.task.log import router as log_router

router = APIRouter(prefix="/task", tags=["Task"])

router.include_router(info_router)
router.include_router(log_router)

__all__ = ["router"]

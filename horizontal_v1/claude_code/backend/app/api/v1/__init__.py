"""
API v1 module.

All API routes are registered here under /api/v1 prefix.

Reference:
- assistant_py/app/v1/__init__.py
- Wiki: API参考文档/API参考文档.md
"""

from fastapi import APIRouter

from app.api.v1.base import router as base_router
from app.api.v1.chat import router as chat_router
from app.api.v1.comm import router as comm_router
from app.api.v1.dict import router as dict_router
from app.api.v1.open import router as open_router
from app.api.v1.resume import router as resume_router
from app.api.v1.rk import router as rk_router
from app.api.v1.task import router as task_router

# Main API v1 router
router = APIRouter()

# Register sub-routers
router.include_router(open_router)   # /api/v1/open/*
router.include_router(comm_router)   # /api/v1/comm/*
router.include_router(dict_router)   # /api/v1/dict/*
router.include_router(base_router)   # /api/v1/base/*
router.include_router(rk_router)     # /api/v1/rk/*
router.include_router(resume_router) # /api/v1/resume/* (AI callbacks)
router.include_router(chat_router)   # /api/v1/chat/* (Dify chat)
router.include_router(task_router)   # /api/v1/task/* (APScheduler tasks)

# Additional routers will be added as modules are implemented:
# - /api/v1/base/sys/user/*     (TODO)
# - /api/v1/base/sys/role/*     (TODO)
# - /api/v1/base/sys/menu/*     (TODO)
# - /api/v1/base/sys/department/* (TODO)

__all__ = ["router"]

"""Base module API router."""

from fastapi import APIRouter

from app.api.v1.base.sys import router as sys_router

router = APIRouter(prefix="/base", tags=["Base"])

router.include_router(sys_router)

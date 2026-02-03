"""Resume analysis callback API router."""

from fastapi import APIRouter

from app.api.v1.resume.callback import router as callback_router

router = APIRouter(prefix="/resume", tags=["Resume"])

router.include_router(callback_router)

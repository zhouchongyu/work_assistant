"""Dict module API router."""

from fastapi import APIRouter

from app.api.v1.dict.info import router as info_router
from app.api.v1.dict.type import router as type_router

router = APIRouter(prefix="/dict", tags=["Dict"])

router.include_router(type_router)
router.include_router(info_router)

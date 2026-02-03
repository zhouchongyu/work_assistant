from fastapi import APIRouter

from backend.app.core.responses import success

router = APIRouter()


@router.get("/health")
async def health():
    return success({"status": "ok"})

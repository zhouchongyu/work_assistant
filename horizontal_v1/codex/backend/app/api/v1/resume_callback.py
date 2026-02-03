from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.deps import get_db_session
from backend.app.core.settings import get_settings
from backend.app.core.responses import success
from backend.app.services.resume_callback_service import process_resume_callback_payload

router = APIRouter(prefix="/resume/analyze", tags=["resume_callback"])


@router.post("/callback")
async def resume_analyze_callback(request: Request, session: AsyncSession = Depends(get_db_session)):
    settings = get_settings()
    token = settings.third_party_callback_token
    if token:
        got = request.headers.get("x-callback-token") or ""
        if got != token:
            raise HTTPException(status_code=403, detail="Forbidden")

    try:
        payload = await request.json()
    except Exception as e:  # noqa: BLE001 - needs to be a 400, not a 500
        raise HTTPException(status_code=400, detail="Invalid JSON") from e

    if isinstance(payload, dict):
        await process_resume_callback_payload(payload, session)

    return success(None)

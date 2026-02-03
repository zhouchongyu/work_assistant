"""
Resume analysis callback API endpoints.

Receives callbacks from third-party AI analysis service.

Reference:
- assistant_py/app/v1/controller/resumeCallbackController.py
- assistant_py/app/v1/service/resume_updater.py
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.response import SuccessResponse, success
from app.services.ai.callback_processor import process_callback_payload

logger = logging.getLogger("work_assistant.resume.callback")

router = APIRouter(prefix="/analyze", tags=["ResumeCallback"])


@router.post("/callback", response_model=None)
async def resume_analyze_callback(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> SuccessResponse:
    """
    Receive third-party resume analysis callback.

    The third-party service calls this endpoint when analysis completes.
    Payload structure depends on the analysis type.
    """
    try:
        payload = await request.json()
        logger.info(f"Received callback: {payload.get('event_type', 'unknown')}")
        await process_callback_payload(payload, db)
    except Exception as e:
        logger.error(f"Failed to process callback: {e}")
        # Still return success to prevent retries from third-party
        # Actual error handling should be done in the processor

    return success()

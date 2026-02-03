"""
Chat API module.

Provides AI chat functionality via Dify integration.
"""

from fastapi import APIRouter

from app.api.v1.chat.conversation import router as conversation_router

router = APIRouter(prefix="/chat", tags=["Chat"])

router.include_router(conversation_router)

__all__ = ["router"]

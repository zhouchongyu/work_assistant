"""
Chat conversation API endpoints.

Provides:
- Chat message sending (blocking and streaming)
- Conversation management
- Message history

Reference:
- cool-admin-midway/src/modules/rk/controller/admin/opportunity.ts
- Wiki: 前端系统/业务模块/其他业务模块/聊天模块.md
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.responses import success_response
from app.middleware.authority import get_current_user
from app.services.chat import dify_client

logger = logging.getLogger("work_assistant.api.chat")

router = APIRouter()


# ==================== Request Schemas ====================

class ChatRequest(BaseModel):
    """Chat message request."""

    content: str = Field(..., description="Message content")
    conversation_id: str | None = Field(None, description="Existing conversation ID")
    inputs: dict[str, Any] | None = Field(None, description="Optional input variables")
    stream: bool = Field(False, description="Enable streaming response")


class ConversationListRequest(BaseModel):
    """Conversation list request."""

    limit: int = Field(20, ge=1, le=100, description="Max items to return")
    last_id: str | None = Field(None, description="Last conversation ID for pagination")


class MessageListRequest(BaseModel):
    """Message list request."""

    conversation_id: str = Field(..., description="Conversation ID")
    limit: int = Field(20, ge=1, le=100, description="Max items to return")
    first_id: str | None = Field(None, description="First message ID for pagination")


class ConversationRenameRequest(BaseModel):
    """Conversation rename request."""

    conversation_id: str = Field(..., description="Conversation ID")
    name: str = Field(..., min_length=1, max_length=200, description="New name")


class FeedbackRequest(BaseModel):
    """Message feedback request."""

    message_id: str = Field(..., description="Message ID")
    rating: str = Field(..., pattern="^(like|dislike)$", description="Rating: like or dislike")


# ==================== Endpoints ====================

@router.post("/message", summary="Send chat message")
async def send_message(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a chat message to the AI.

    - If `stream=false`: Returns complete response
    - If `stream=true`: Returns Server-Sent Events stream
    """
    user_name = current_user.get("username", "anonymous")
    user_id = str(current_user.get("user_id", 0))

    # Prepare inputs with user context
    inputs = body.inputs or {}
    inputs["userId"] = user_id
    inputs["userName"] = user_name

    if body.stream:
        # Streaming response
        async def generate():
            async for chunk in dify_client.chat_stream(
                query=body.content,
                user=user_name,
                inputs=inputs,
                conversation_id=body.conversation_id,
            ):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    else:
        # Blocking response
        result = await dify_client.chat(
            query=body.content,
            user=user_name,
            inputs=inputs,
            conversation_id=body.conversation_id,
        )
        return success_response(data=result)


@router.post("/conversations", summary="Get conversation list")
async def get_conversations(
    body: ConversationListRequest,
    current_user: dict = Depends(get_current_user),
):
    """Get list of conversations for the current user."""
    user_name = current_user.get("username", "anonymous")

    result = await dify_client.get_conversations(
        user=user_name,
        limit=body.limit,
        last_id=body.last_id,
    )
    return success_response(data=result)


@router.post("/messages", summary="Get messages in conversation")
async def get_messages(
    body: MessageListRequest,
    current_user: dict = Depends(get_current_user),
):
    """Get messages in a specific conversation."""
    user_name = current_user.get("username", "anonymous")

    result = await dify_client.get_messages(
        user=user_name,
        conversation_id=body.conversation_id,
        limit=body.limit,
        first_id=body.first_id,
    )
    return success_response(data=result)


@router.post("/conversation/rename", summary="Rename conversation")
async def rename_conversation(
    body: ConversationRenameRequest,
    current_user: dict = Depends(get_current_user),
):
    """Rename a conversation."""
    user_name = current_user.get("username", "anonymous")

    result = await dify_client.rename_conversation(
        user=user_name,
        conversation_id=body.conversation_id,
        name=body.name,
    )
    return success_response(data=result)


@router.post("/conversation/delete", summary="Delete conversation")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a conversation."""
    user_name = current_user.get("username", "anonymous")

    await dify_client.delete_conversation(
        user=user_name,
        conversation_id=conversation_id,
    )
    return success_response(message="Conversation deleted")


@router.post("/feedback", summary="Submit message feedback")
async def submit_feedback(
    body: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """Submit feedback (like/dislike) for a message."""
    user_name = current_user.get("username", "anonymous")

    result = await dify_client.feedback(
        message_id=body.message_id,
        user=user_name,
        rating=body.rating,
    )
    return success_response(data=result)


# ==================== Workflow Endpoints ====================

class WorkflowRequest(BaseModel):
    """Workflow execution request."""

    inputs: dict[str, Any] = Field(..., description="Workflow input variables")
    stream: bool = Field(False, description="Enable streaming response")


@router.post("/workflow", summary="Execute workflow")
async def execute_workflow(
    body: WorkflowRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a Dify workflow.

    - If `stream=false`: Returns complete result
    - If `stream=true`: Returns Server-Sent Events stream
    """
    user_name = current_user.get("username", "anonymous")

    if body.stream:
        async def generate():
            async for chunk in dify_client.workflows_stream(
                inputs=body.inputs,
                user=user_name,
            ):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    else:
        result = await dify_client.workflows(
            inputs=body.inputs,
            user=user_name,
        )
        return success_response(data=result)

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.app.core.responses import business_error, success
from backend.app.core.security import CurrentUser, get_current_user
from backend.app.integrations.dify.client import DifyClient, DifyClientError, get_dify_client
from backend.app.schemas.chat import (
    ChatMessagesDetailRequest,
    ChatMessagesRequest,
    ChatRequest,
    ChatResult,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    current: CurrentUser = Depends(get_current_user),
    dify: DifyClient = Depends(get_dify_client),
):
    _ = current
    response_mode = (payload.response_mode or "streaming").lower()
    if response_mode == "blocking":
        try:
            res = await dify.chat_blocking(
                query=payload.content,
                user=str(current.user.id),
                inputs=payload.inputs or {},
                conversation_id=payload.conversation_id,
            )
        except DifyClientError as e:
            return business_error(str(e))
        return success(
            ChatResult(
                answer=res.answer,
                conversation_id=res.conversation_id,
                message_id=res.message_id,
            )
        )

    async def _stream():
        try:
            stream = await dify.chat_streaming(
                query=payload.content,
                user=str(current.user.id),
                inputs=payload.inputs or {},
                conversation_id=payload.conversation_id,
            )
            async for chunk in stream:
                text = chunk.decode() if isinstance(chunk, (bytes, bytearray)) else str(chunk)
                yield f"data: {text}\n\n"
        except DifyClientError as e:
            yield f"event: error\ndata: {str(e)}\n\n"
        yield "event: end\ndata: [DONE]\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")


@router.post("/messages")
async def list_conversations(
    payload: ChatMessagesRequest,
    current: CurrentUser = Depends(get_current_user),
    dify: DifyClient = Depends(get_dify_client),
):
    _ = current
    try:
        data = await dify.list_conversations(user=str(current.user.id), last_id=payload.last_id, limit=payload.limit)
    except DifyClientError as e:
        return business_error(str(e))
    conversations = data.get("data") or data.get("result") or []
    return success(conversations)


@router.post("/messages_detail")
async def list_messages_detail(
    payload: ChatMessagesDetailRequest,
    current: CurrentUser = Depends(get_current_user),
    dify: DifyClient = Depends(get_dify_client),
):
    _ = current
    try:
        data = await dify.list_messages(user=str(current.user.id), conversation_id=payload.conversation_id)
    except DifyClientError as e:
        return business_error(str(e))
    messages = data.get("data") or data.get("result") or []
    return success(messages)

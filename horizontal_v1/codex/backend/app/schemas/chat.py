from __future__ import annotations

from typing import Any

from backend.app.schemas.base import Schema


class ChatRequest(Schema):
    content: str
    conversation_id: str | None = None
    response_mode: str = "streaming"
    inputs: dict[str, Any] | None = None


class ChatResult(Schema):
    answer: str | None = None
    conversation_id: str | None = None
    message_id: str | None = None


class ChatMessagesRequest(Schema):
    limit: int = 20
    last_id: str | None = None


class ChatMessagesDetailRequest(Schema):
    conversation_id: str

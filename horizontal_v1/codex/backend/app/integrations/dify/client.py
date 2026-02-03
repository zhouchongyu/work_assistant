from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from backend.app.core.request_id import get_request_id
from backend.app.core.settings import get_settings


class DifyClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class DifyChatResult:
    answer: str | None
    conversation_id: str | None
    message_id: str | None
    raw: dict


class DifyClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_ms: int = 60_000):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_ms = timeout_ms

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "x-request-id": get_request_id(),
        }

    async def chat_blocking(
        self,
        *,
        query: str,
        user: str,
        inputs: dict | None = None,
        conversation_id: str | None = None,
    ) -> DifyChatResult:
        url = f"{self._base_url}/chat-messages"
        payload: dict = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "blocking",
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        async with httpx.AsyncClient(timeout=self._timeout_ms / 1000) as client:
            resp = await client.post(url, json=payload, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        if not isinstance(data, dict):
            raise DifyClientError("Unexpected Dify response")
        return DifyChatResult(
            answer=data.get("answer"),
            conversation_id=data.get("conversation_id") or data.get("conversationId"),
            message_id=data.get("message_id") or data.get("messageId"),
            raw=data,
        )

    async def chat_streaming(
        self,
        *,
        query: str,
        user: str,
        inputs: dict | None = None,
        conversation_id: str | None = None,
    ) -> AsyncIterator[bytes]:
        url = f"{self._base_url}/chat-messages"
        payload: dict = {
            "query": query,
            "inputs": inputs or {},
            "user": user,
            "response_mode": "streaming",
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        headers = self._headers()
        headers.pop("Content-Type", None)

        async def _iter():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        return _iter()

    async def list_conversations(self, *, user: str, last_id: str | None, limit: int) -> dict:
        url = f"{self._base_url}/conversations"
        params = {"user": user, "limit": int(limit)}
        if last_id:
            params["last_id"] = last_id
        async with httpx.AsyncClient(timeout=self._timeout_ms / 1000) as client:
            resp = await client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        if not isinstance(data, dict):
            raise DifyClientError("Unexpected Dify response")
        return data

    async def list_messages(self, *, user: str, conversation_id: str) -> dict:
        url = f"{self._base_url}/messages"
        params = {"user": user, "conversation_id": conversation_id}
        async with httpx.AsyncClient(timeout=self._timeout_ms / 1000) as client:
            resp = await client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        if not isinstance(data, dict):
            raise DifyClientError("Unexpected Dify response")
        return data


def get_dify_client() -> DifyClient:
    settings = get_settings()
    return DifyClient(
        base_url=settings.dify_api_base_url,
        api_key=settings.dify_api_key,
        timeout_ms=settings.dify_timeout_ms,
    )


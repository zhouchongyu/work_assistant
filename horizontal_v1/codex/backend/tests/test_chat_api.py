from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient


async def _login(client: AsyncClient, app) -> str:
    captcha_id = str(uuid.uuid4())
    await app.state._test_redis.set(f"verify:img:{captcha_id}", "abcd", ex=1800)
    res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "admin123",
            "captchaId": captcha_id,
            "verifyCode": "abcd",
        },
    )
    body = res.json()
    assert res.status_code == 200
    assert body["code"] == 1000
    return body["result"]["token"]


@pytest.mark.anyio
async def test_chat_blocking(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        res = await client.post(
            "/api/v1/chat/chat",
            json={"content": "hi", "responseMode": "blocking", "inputs": {"a": 1}},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 1000
        assert body["result"]["answer"] == "hi-blocking"
        assert body["result"]["conversationId"] == "c-test"
        assert body["result"]["messageId"] == "m-test"


@pytest.mark.anyio
async def test_chat_streaming_sse(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        res = await client.post(
            "/api/v1/chat/chat",
            json={"content": "stream please", "responseMode": "streaming"},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/event-stream")
        text = res.text
        assert "chunk-1" in text
        assert "chunk-2" in text
        assert "event: end" in text


@pytest.mark.anyio
async def test_chat_list_conversations(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        res = await client.post(
            "/api/v1/chat/messages",
            json={"limit": 10, "lastId": None},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 1000
        assert isinstance(body["result"], list)
        assert body["result"][0]["id"] == "c-test"


@pytest.mark.anyio
async def test_chat_list_messages_detail(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        res = await client.post(
            "/api/v1/chat/messages_detail",
            json={"conversationId": "c-test"},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 1000
        assert isinstance(body["result"], list)
        assert body["result"][0]["id"] == "m-test"

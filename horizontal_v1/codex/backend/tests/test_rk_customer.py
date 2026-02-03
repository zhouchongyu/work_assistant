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
    return res.json()["result"]["token"]


@pytest.mark.anyio
async def test_rk_customer_add_and_page(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        add_res = await client.post(
            "/api/v1/rk/customer/add",
            headers={"Authorization": token},
            json={"name": "ACME"},
        )
        assert add_res.status_code == 200
        add_body = add_res.json()
        assert add_body["code"] == 1000
        assert add_body["result"]["name"] == "ACME"

        page_res = await client.post(
            "/api/v1/rk/customer/page",
            headers={"Authorization": token},
            json={"page": 1, "size": 20},
        )
        assert page_res.status_code == 200
        page_body = page_res.json()
        assert page_body["code"] == 1000
        assert page_body["result"]["pagination"]["total"] == 1
        assert page_body["result"]["list"][0]["name"] == "ACME"


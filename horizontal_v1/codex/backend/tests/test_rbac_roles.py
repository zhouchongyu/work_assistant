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
    assert res.status_code == 200
    body = res.json()
    assert body["code"] == 1000
    return body["result"]["token"]


@pytest.mark.anyio
async def test_rbac_roles_add_page_and_list(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        add_res = await client.post(
            "/api/v1/rbac/roles/add",
            headers=headers,
            json={"name": "Manager", "label": "manager", "remark": "mgr", "relevance": False},
        )
        assert add_res.status_code == 200
        add_body = add_res.json()
        assert add_body["code"] == 1000
        role_id = add_body["result"]["id"]

        page_res = await client.post(
            "/api/v1/rbac/roles/page",
            headers=headers,
            json={"page": 1, "size": 10, "keyWord": "Man"},
        )
        assert page_res.status_code == 200
        page_body = page_res.json()
        assert page_body["code"] == 1000
        assert page_body["result"]["pagination"]["total"] >= 1
        assert any(r["id"] == role_id for r in page_body["result"]["list"])

        list_res = await client.post("/api/v1/rbac/roles/list", headers=headers, json={})
        assert list_res.status_code == 200
        list_body = list_res.json()
        assert list_body["code"] == 1000
        assert any(r["id"] == role_id for r in list_body["result"])


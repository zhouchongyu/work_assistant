from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_login_me_and_rbac_flow(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        captcha_id = str(uuid.uuid4())
        await app.state._test_redis.set(f"verify:img:{captcha_id}", "abcd", ex=1800)

        login_res = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123",
                "captchaId": captcha_id,
                "verifyCode": "abcd",
            },
        )
        assert login_res.status_code == 200
        login_body = login_res.json()
        assert login_body["code"] == 1000
        assert login_body["message"] == "success"
        assert "token" in login_body["result"]
        assert "refreshToken" in login_body["result"]
        assert login_res.headers["x-request-id"] == login_body["request_id"]

        token = login_body["result"]["token"]

        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": token})
        assert me_res.status_code == 200
        me_body = me_res.json()
        assert me_body["code"] == 1000
        assert me_body["result"]["username"] == "admin"

        perms_res = await client.get("/api/v1/rbac/perms", headers={"Authorization": token})
        assert perms_res.status_code == 200
        perms_body = perms_res.json()
        assert perms_body["code"] == 1000
        assert isinstance(perms_body["result"], list)

        menus_res = await client.get("/api/v1/rbac/menus", headers={"Authorization": token})
        assert menus_res.status_code == 200
        menus_body = menus_res.json()
        assert menus_body["code"] == 1000
        assert isinstance(menus_body["result"], list)

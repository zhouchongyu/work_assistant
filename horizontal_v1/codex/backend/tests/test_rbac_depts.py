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
async def test_rbac_depts_crud_and_tree(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        add_root = await client.post(
            "/api/v1/rbac/depts/add",
            headers=headers,
            json={"name": "HQ", "parentId": None, "orderNum": 0},
        )
        assert add_root.status_code == 200
        root_body = add_root.json()
        assert root_body["code"] == 1000
        root_id = root_body["result"]["id"]

        add_child = await client.post(
            "/api/v1/rbac/depts/add",
            headers=headers,
            json={"name": "IT", "parentId": root_id, "orderNum": 0},
        )
        assert add_child.status_code == 200
        child_body = add_child.json()
        assert child_body["code"] == 1000
        child_id = child_body["result"]["id"]

        list_res = await client.post("/api/v1/rbac/depts/list", headers=headers, json={})
        assert list_res.status_code == 200
        list_body = list_res.json()
        assert list_body["code"] == 1000
        assert any(d["name"] == "HQ" for d in list_body["result"])
        assert any(d["name"] == "IT" and d["parentId"] == root_id for d in list_body["result"])

        tree_res = await client.post("/api/v1/rbac/depts/tree", headers=headers, json={})
        assert tree_res.status_code == 200
        tree_body = tree_res.json()
        assert tree_body["code"] == 1000
        assert tree_body["result"][0]["name"] == "HQ"
        assert tree_body["result"][0]["children"][0]["name"] == "IT"

        order_res = await client.post(
            "/api/v1/rbac/depts/order",
            headers=headers,
            json=[
                {"id": root_id, "parentId": None, "orderNum": 0},
                {"id": child_id, "parentId": root_id, "orderNum": 1},
            ],
        )
        assert order_res.status_code == 200
        assert order_res.json()["code"] == 1000

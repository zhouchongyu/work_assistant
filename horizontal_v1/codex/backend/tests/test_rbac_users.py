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
async def test_rbac_users_add_page_update_disable_and_move(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        role_res = await client.post(
            "/api/v1/rbac/roles/add",
            headers=headers,
            json={"name": "Manager2", "label": "manager2", "relevance": False},
        )
        assert role_res.status_code == 200
        role_id = role_res.json()["result"]["id"]

        dept_res = await client.post(
            "/api/v1/rbac/depts/add",
            headers=headers,
            json={"name": "DeptA", "parentId": None, "orderNum": 0},
        )
        assert dept_res.status_code == 200
        dept_id = dept_res.json()["result"]["id"]

        add_res = await client.post(
            "/api/v1/rbac/users/add",
            headers=headers,
            json={
                "username": "user1",
                "password": "pass1234",
                "name": "User One",
                "departmentId": dept_id,
                "roleIdList": [role_id],
                "status": 1,
            },
        )
        assert add_res.status_code == 200
        add_body = add_res.json()
        assert add_body["code"] == 1000
        user_id = add_body["result"]["id"]

        page_res = await client.post(
            "/api/v1/rbac/users/page",
            headers=headers,
            json={"page": 1, "size": 10, "keyWord": "user1"},
        )
        assert page_res.status_code == 200
        page_body = page_res.json()
        assert page_body["code"] == 1000
        assert any(u["id"] == user_id for u in page_body["result"]["list"])

        upd_res = await client.post(
            "/api/v1/rbac/users/update",
            headers=headers,
            json={"id": user_id, "nickName": "U1", "phone": "123", "roleIdList": [role_id]},
        )
        assert upd_res.status_code == 200
        upd_body = upd_res.json()
        assert upd_body["code"] == 1000
        assert upd_body["result"]["id"] == user_id

        move_dept_res = await client.post(
            "/api/v1/rbac/depts/add",
            headers=headers,
            json={"name": "DeptB", "parentId": None, "orderNum": 0},
        )
        assert move_dept_res.status_code == 200
        dept_b_id = move_dept_res.json()["result"]["id"]

        move_res = await client.post(
            "/api/v1/rbac/users/move",
            headers=headers,
            json={"departmentId": dept_b_id, "userIds": [user_id]},
        )
        assert move_res.status_code == 200
        assert move_res.json()["code"] == 1000

        disable_res = await client.post(
            "/api/v1/rbac/users/disable",
            headers=headers,
            json={"id": user_id, "status": 0},
        )
        assert disable_res.status_code == 200
        assert disable_res.json()["code"] == 1000


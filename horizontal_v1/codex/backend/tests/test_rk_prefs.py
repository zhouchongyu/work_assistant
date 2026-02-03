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
async def test_rk_customer_column_prefs(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        name = "column-custom__test"
        get0 = await client.get("/api/v1/rk/customer_column/get_column_info", headers=headers, params={"name": name})
        assert get0.status_code == 200
        assert get0.json()["code"] == 1000
        assert get0.json()["result"] is None

        set1 = await client.post(
            "/api/v1/rk/customer_column/set_column_info",
            headers=headers,
            json={"name": name, "info": [{"label": "姓名", "prop": "name", "checked": True, "orderNum": 0}]},
        )
        assert set1.status_code == 200
        assert set1.json()["code"] == 1000
        assert set1.json()["result"] is True

        get1 = await client.get("/api/v1/rk/customer_column/get_column_info", headers=headers, params={"name": name})
        assert get1.status_code == 200
        assert get1.json()["code"] == 1000
        assert get1.json()["result"][0]["prop"] == "name"

        del1 = await client.post(
            "/api/v1/rk/customer_column/delete_column_info", headers=headers, json={"name": name}
        )
        assert del1.status_code == 200
        assert del1.json()["code"] == 1000
        assert del1.json()["result"] is True

        get2 = await client.get("/api/v1/rk/customer_column/get_column_info", headers=headers, params={"name": name})
        assert get2.status_code == 200
        assert get2.json()["code"] == 1000
        assert get2.json()["result"] is None


@pytest.mark.anyio
async def test_rk_active_switch_and_page_filtering(app):
    # Seed: one inactive customer in DB
    from backend.app.db.session import get_async_sessionmaker
    from backend.app.models.rk_customer import RkCustomer

    async_session = get_async_sessionmaker()
    async with async_session() as session:
        session.add(
            RkCustomer(
                name="Inactive Customer",
                code="C0",
                active=False,
                to_be_confirmed=False,
                created_by=1,
                updated_by=1,
                owner_id=1,
                department_id=None,
            )
        )
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        get0 = await client.get("/api/v1/rk/active/get_switch", headers=headers)
        assert get0.status_code == 200
        assert get0.json()["code"] == 1000
        assert get0.json()["result"]["status"] is False

        set1 = await client.post("/api/v1/rk/active/active_switch", headers=headers, json={"status": True})
        assert set1.status_code == 200
        assert set1.json()["code"] == 1000
        assert set1.json()["result"]["status"] is True

        get1 = await client.get("/api/v1/rk/active/get_switch", headers=headers)
        assert get1.status_code == 200
        assert get1.json()["result"]["status"] is True

        # activeSwitch = false => show all (includes inactive)
        page_all = await client.post(
            "/api/v1/rk/customer/page",
            headers=headers,
            json={"page": 1, "size": 200, "activeSwitch": False},
        )
        assert page_all.status_code == 200
        assert any(c["name"] == "Inactive Customer" for c in page_all.json()["result"]["list"])

        # activeSwitch = true => filter active=true (excludes inactive)
        page_active = await client.post(
            "/api/v1/rk/customer/page",
            headers=headers,
            json={"page": 1, "size": 200, "activeSwitch": True},
        )
        assert page_active.status_code == 200
        assert not any(c["name"] == "Inactive Customer" for c in page_active.json()["result"]["list"])


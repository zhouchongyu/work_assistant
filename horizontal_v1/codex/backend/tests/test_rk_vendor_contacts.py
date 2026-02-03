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
async def test_rk_vendor_and_contacts_crud(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        vendor_add = await client.post(
            "/api/v1/rk/vendor/add",
            headers=headers,
            json={"name": "Vendor A", "code": "V001"},
        )
        assert vendor_add.status_code == 200
        vendor_id = vendor_add.json()["result"]["id"]

        vc_add = await client.post(
            "/api/v1/rk/vendor_contact/add",
            headers=headers,
            json={"vendorId": vendor_id, "name": "Alice", "email": "a@example.com", "default": True},
        )
        assert vc_add.status_code == 200
        vc_id = vc_add.json()["result"]["id"]

        vc_list = await client.get(
            "/api/v1/rk/vendor_contact/list", headers=headers, params={"vendorId": vendor_id}
        )
        assert vc_list.status_code == 200
        assert any(c["id"] == vc_id for c in vc_list.json()["result"])

        vc_update = await client.post(
            "/api/v1/rk/vendor_contact/update",
            headers=headers,
            json={"id": vc_id, "vendorId": vendor_id, "phone": "123"},
        )
        assert vc_update.status_code == 200
        assert vc_update.json()["code"] == 1000

        customer_add = await client.post(
            "/api/v1/rk/customer/add",
            headers=headers,
            json={"name": "Customer A", "code": "C001"},
        )
        assert customer_add.status_code == 200
        customer_id = customer_add.json()["result"]["id"]

        cc_add = await client.post(
            "/api/v1/rk/customer_contact/add",
            headers=headers,
            json={"customerId": customer_id, "name": "Bob", "email": "b@example.com", "default": True},
        )
        assert cc_add.status_code == 200
        cc_id = cc_add.json()["result"]["id"]

        cc_list = await client.get(
            "/api/v1/rk/customer_contact/list", headers=headers, params={"customerId": customer_id}
        )
        assert cc_list.status_code == 200
        assert any(c["id"] == cc_id for c in cc_list.json()["result"])


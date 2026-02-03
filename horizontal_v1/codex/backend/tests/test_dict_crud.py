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
async def test_dict_type_info_crud_and_cache_invalidation(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)
        headers = {"Authorization": token}

        add_type = await client.post(
            "/api/v1/dict/type/add",
            headers=headers,
            json={"name": "品牌", "key": "brand", "page": None},
        )
        assert add_type.status_code == 200
        type_body = add_type.json()
        assert type_body["code"] == 1000
        type_id = type_body["result"]["id"]

        add_info = await client.post(
            "/api/v1/dict/info/add",
            headers=headers,
            json={
                "typeId": type_id,
                "name": "COOL",
                "value": "cool",
                "orderNum": 1,
                "isShow": True,
                "isProcess": True,
            },
        )
        assert add_info.status_code == 200
        info_body = add_info.json()
        assert info_body["code"] == 1000
        info_id = info_body["result"]["id"]

        # Populate cache via app endpoint
        res1 = await client.post(
            "/api/v1/dict/info/data",
            headers=headers,
            json={"types": ["brand"]},
        )
        assert res1.status_code == 200
        body1 = res1.json()
        assert body1["code"] == 1000
        assert body1["result"]["brand_undefined"][0]["name"] == "COOL"

        cache_key = "dict:data:brand_undefined"
        assert await app.state._test_redis.get(cache_key) is not None

        # Update dict info should invalidate cache
        upd_info = await client.post(
            "/api/v1/dict/info/update",
            headers=headers,
            json={"id": info_id, "name": "COOL2"},
        )
        assert upd_info.status_code == 200
        assert upd_info.json()["code"] == 1000

        assert await app.state._test_redis.get(cache_key) is None

        # Subsequent fetch should see new value + repopulate cache
        res2 = await client.post(
            "/api/v1/dict/info/data",
            headers=headers,
            json={"types": ["brand"]},
        )
        assert res2.status_code == 200
        body2 = res2.json()
        assert body2["result"]["brand_undefined"][0]["name"] == "COOL2"
        assert await app.state._test_redis.get(cache_key) is not None


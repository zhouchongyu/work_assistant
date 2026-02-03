from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete


@pytest.mark.anyio
async def test_dict_data_read_through_cache(app):
    # Seed dict type/info
    from backend.app.db.session import get_async_sessionmaker
    from backend.app.models.dict_info import DictInfo
    from backend.app.models.dict_type import DictType

    async_session = get_async_sessionmaker()
    async with async_session() as session:
        dtype = DictType(name="品牌", key="brand", page=None)
        session.add(dtype)
        await session.flush()

        dinfo = DictInfo(type_id=dtype.id, name="COOL", value="cool", order_num=1)
        session.add(dinfo)
        await session.commit()

    # Login to access dict endpoint
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
        token = login_res.json()["result"]["token"]

        # First call populates cache
        res1 = await client.post(
            "/api/v1/dict/info/data",
            headers={"Authorization": token},
            json={"types": ["brand"]},
        )
        assert res1.status_code == 200
        body1 = res1.json()
        assert body1["code"] == 1000
        assert "brand_undefined" in body1["result"]
        assert body1["result"]["brand_undefined"][0]["name"] == "COOL"

        cached = await app.state._test_redis.get("dict:data:brand_undefined")
        assert cached is not None

        # Delete DB rows to prove second call hits cache
        async with async_session() as session:
            await session.execute(delete(DictInfo))
            await session.commit()

        res2 = await client.post(
            "/api/v1/dict/info/data",
            headers={"Authorization": token},
            json={"types": ["brand"]},
        )
        assert res2.status_code == 200
        body2 = res2.json()
        assert body2["result"]["brand_undefined"][0]["name"] == "COOL"


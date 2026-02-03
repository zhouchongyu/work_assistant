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
async def test_sharepoint_create_folder_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        res = await client.post(
            "/api/v1/sharepoint/create_folder",
            json={"folderName": "Vendor A_1"},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 1000
        assert body["result"]["folderId"]
        assert body["result"]["folderUrl"]


@pytest.mark.anyio
async def test_vendor_add_sets_sharepoint_folder(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_add = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor SP", "code": "VSP"},
            headers={"Authorization": token},
        )
        assert vendor_add.status_code == 200
        vendor_id = int(vendor_add.json()["result"]["id"])

        from sqlalchemy import select

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_vendor import RkVendor

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            vendor = (await session.execute(select(RkVendor).where(RkVendor.id == vendor_id))).scalar_one()
            assert vendor.folder_id
            assert vendor.folder_url


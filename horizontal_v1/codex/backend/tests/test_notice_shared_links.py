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
    body = res.json()
    assert res.status_code == 200
    assert body["code"] == 1000
    return body["result"]["token"]


@pytest.mark.anyio
async def test_notice_unread_count_page_and_mark_read(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_notice import RkNotice

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            n1 = RkNotice(receiver_id=1, content="Hello", is_read=False, created_by=1, owner_id=1, active=True)
            n2 = RkNotice(receiver_id=1, content="World", is_read=False, created_by=1, owner_id=1, active=True)
            session.add_all([n1, n2])
            await session.flush()
            n1_id = int(n1.id)
            await session.commit()

        unread = await client.get("/api/v1/notice/unread_count", headers={"Authorization": token})
        assert unread.status_code == 200
        unread_body = unread.json()
        assert unread_body["code"] == 1000
        assert unread_body["result"] == 2

        page = await client.post(
            "/api/v1/notice/page",
            json={"page": 1, "size": 20},
            headers={"Authorization": token},
        )
        assert page.status_code == 200
        page_body = page.json()
        assert page_body["code"] == 1000
        assert page_body["result"]["pagination"]["total"] == 2

        mark = await client.post(
            "/api/v1/notice/mark_read",
            json={"ids": [n1_id]},
            headers={"Authorization": token},
        )
        assert mark.status_code == 200
        assert mark.json()["code"] == 1000

        unread2 = await client.get("/api/v1/notice/unread_count", headers={"Authorization": token})
        assert unread2.status_code == 200
        assert unread2.json()["result"] == 1


@pytest.mark.anyio
async def test_shared_links_create_list_and_preview(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor C", "code": "V003"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        file_bytes = b"share me"
        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", file_bytes, "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        create = await client.post(
            "/api/v1/shared_links/create",
            json={"ids": [supply_id], "type": "supply"},
            headers={"Authorization": token},
        )
        assert create.status_code == 200
        create_body = create.json()
        assert create_body["code"] == 1000
        share_token = create_body["result"]["shareToken"]

        lst = await client.post(
            "/api/v1/shared_links/shared_links_list",
            json={"shareToken": share_token, "type": "supply"},
        )
        assert lst.status_code == 200
        lst_body = lst.json()
        assert lst_body["code"] == 1000
        assert len(lst_body["result"]) == 1
        assert lst_body["result"][0]["id"] == supply_id

        preview = await client.get(f"/api/v1/shared_links/resume_preview/{share_token}-{supply_id}")
        assert preview.status_code == 200
        assert preview.content == file_bytes

        tmp = await client.post(
            "/api/v1/shared_links/get_tmp_url",
            json={"supplyId": supply_id},
            headers={"Authorization": token},
        )
        assert tmp.status_code == 200
        tmp_body = tmp.json()
        assert tmp_body["code"] == 1000
        code = tmp_body["result"]["code"]

        tmp_preview = await client.get(f"/api/v1/shared_links/resume_tmp_preview/{code}")
        assert tmp_preview.status_code == 200
        assert tmp_preview.content == file_bytes


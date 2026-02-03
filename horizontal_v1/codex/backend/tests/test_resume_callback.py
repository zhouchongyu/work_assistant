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
async def test_resume_callback_updates_supply_and_persists_llm_data(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor CB", "code": "VCB"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"cb resume", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        cb = await client.post(
            "/api/v1/resume/analyze/callback",
            json={
                "eventType": "resume",
                "extUniqueId": supply_id,
                "analysis": {"stopErr": False, "parsed": {"name": "Alice"}},
                "extraData": {"version": 1},
                "llmRaws": [
                    {
                        "eventType": "supply_basic",
                        "res": {"generated_output": {"result": {"name": "Alice"}}},
                        "model": "mock",
                        "special": "",
                        "parentId": 1,
                        "thirdId": 2,
                        "context": {"source": "test"},
                    }
                ],
            },
        )
        assert cb.status_code == 200
        assert cb.json()["code"] == 1000

        from sqlalchemy import select

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_llm_data import RkLlmData
        from backend.app.models.rk_supply import RkSupply
        from backend.app.models.rk_supply_ai import RkSupplyAi

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            supply = (await session.execute(select(RkSupply).where(RkSupply.id == supply_id))).scalar_one()
            assert supply.analysis_status == "analysis_done"

            ai = (await session.execute(select(RkSupplyAi).where(RkSupplyAi.supply_id == supply_id))).scalar_one()
            assert ai.basic and ai.basic.get("parsed", {}).get("name") == "Alice"

            llm = (
                await session.execute(select(RkLlmData).where(RkLlmData.supply_id == supply_id))
            ).scalars().all()
            assert any(r.event_type == "supply_basic" for r in llm)


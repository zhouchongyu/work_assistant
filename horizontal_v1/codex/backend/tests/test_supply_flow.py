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
async def test_supply_upload_triggers_third_party_resume_analyze(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor TP", "code": "VTP"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        file_bytes = b"resume bytes"
        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", file_bytes, "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        assert upload.status_code == 200
        body = upload.json()
        assert body["code"] == 1000

        supply_id = body["result"]["supplyId"]
        calls = app.state._test_third_party.calls["analyze_resume"]
        assert len(calls) == 1
        assert calls[0]["supply_id"] == supply_id
        assert calls[0]["version"] == 1


@pytest.mark.anyio
async def test_supply_update_file_triggers_third_party_resume_analyze(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor TP2", "code": "VTP2"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        update = await client.post(
            "/api/v1/supply/update_file",
            files={"file": ("resume-v2.pdf", b"v2", "application/pdf")},
            data={"supply_id": str(supply_id), "version": "2"},
            headers={"Authorization": token},
        )
        assert update.status_code == 200
        assert update.json()["code"] == 1000

        calls = app.state._test_third_party.calls["analyze_resume"]
        assert len(calls) == 2
        assert calls[-1]["supply_id"] == supply_id
        assert calls[-1]["version"] == 2


@pytest.mark.anyio
async def test_supply_update_resume_proposal_triggers_third_party_proposal_analyze(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor TP3", "code": "VTP3"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        res = await client.post(
            "/api/v1/supply/update_resume_proposal",
            json={"supplyId": supply_id, "proposalDocument": "hello"},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        assert res.json()["code"] == 1000

        calls = app.state._test_third_party.calls["analyze_resume_proposal"]
        assert len(calls) == 1
        assert calls[0]["supply_id"] == supply_id


@pytest.mark.anyio
async def test_supply_update_demand_txt_triggers_third_party_demand_analyze(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_demand import RkDemand

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            demand = RkDemand(
                name="Demand TP",
                code="DTP",
                remark="old",
                created_by=1,
                updated_by=1,
                owner_id=1,
                active=True,
                version=1,
            )
            session.add(demand)
            await session.flush()
            demand_id = int(demand.id)
            await session.commit()

        res = await client.post(
            "/api/v1/supply/update_demand_txt",
            json={"demandId": demand_id, "demandTxt": "new", "version": 2},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        assert res.json()["code"] == 1000

        calls = app.state._test_third_party.calls["analyze_demand_txt"]
        assert len(calls) == 1
        assert calls[0]["demand_id"] == demand_id
        assert calls[0]["version"] == 2


@pytest.mark.anyio
async def test_supply_match_start_is_best_effort_when_third_party_errors(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor B2", "code": "V002B"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"resume v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_demand import RkDemand

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            demand = RkDemand(
                name="Demand 2",
                code="D002",
                created_by=1,
                updated_by=1,
                owner_id=1,
                active=True,
                version=1,
            )
            session.add(demand)
            await session.flush()
            demand_id = int(demand.id)
            await session.commit()

        async def _boom(**kwargs):
            _ = kwargs
            raise RuntimeError("boom")

        app.state._test_third_party.analyze_match = _boom

        match_res = await client.post(
            "/api/v1/supply/match_start",
            json={
                "demandId": demand_id,
                "supplyIds": [supply_id],
                "roleList": [],
                "flagData": [],
            },
            headers={"Authorization": token},
        )
        assert match_res.status_code == 200
        assert match_res.json()["code"] == 1000


@pytest.mark.anyio
async def test_supply_change_file_name_updates_sharepoint_item(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor Rename", "code": "VRN"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        from sqlalchemy import select

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_supply import RkSupply

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            supply = (await session.execute(select(RkSupply).where(RkSupply.id == supply_id))).scalar_one()
            file_id = supply.file_id
            assert file_id

        new_name = "resume-renamed.pdf"
        res = await client.post(
            "/api/v1/supply/change_supply_file_name",
            json={"supplyId": supply_id, "newName": new_name},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        assert res.json()["code"] == 1000

        file_state = app.state._test_graph._files[str(file_id)]
        assert file_state[2] == new_name


@pytest.mark.anyio
async def test_supply_update_case_hard_condition_persists_warning_messages(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor HC", "code": "VHC"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        from sqlalchemy import select

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_demand import RkDemand
        from backend.app.models.rk_supply_demand_link import RkSupplyDemandLink

        async def _hard_condition(**kwargs):
            app.state._test_third_party.calls["hard_condition"].append(kwargs)
            return {"msg": [{"zh": "A"}, {"zh": "B"}]}

        app.state._test_third_party.hard_condition = _hard_condition

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            demand = RkDemand(
                name="Demand HC",
                code="DHC",
                price=100,
                japanese_level="N2",
                english_level="B2",
                citizenship="1",
                created_by=1,
                updated_by=1,
                owner_id=1,
                active=True,
                version=1,
            )
            session.add(demand)
            await session.flush()
            demand_id = int(demand.id)

            session.add(RkSupplyDemandLink(demand_id=demand_id, supply_id=supply_id, demand_version=1, supply_version=1))
            await session.commit()

        res = await client.post(
            "/api/v1/supply/update_case_hard_condition",
            json={"demandId": demand_id, "supplyId": supply_id},
            headers={"Authorization": token},
        )
        assert res.status_code == 200
        assert res.json()["code"] == 1000

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            case = (
                await session.execute(
                    select(RkSupplyDemandLink).where(
                        RkSupplyDemandLink.demand_id == demand_id,
                        RkSupplyDemandLink.supply_id == supply_id,
                    )
                )
            ).scalar_one()
            assert case.warning_msg == ["A", "B"]


@pytest.mark.anyio
async def test_supply_upload_and_duplicate_detection(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor A", "code": "V001"},
            headers={"Authorization": token},
        )
        assert vendor_res.status_code == 200
        vendor_id = vendor_res.json()["result"]["id"]

        file_bytes = b"hello resume"
        upload1 = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", file_bytes, "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        assert upload1.status_code == 200
        body1 = upload1.json()
        assert body1["code"] == 1000
        assert body1["result"]["url"].startswith("https://sharepoint.test/share/")
        supply1_id = body1["result"]["supplyId"]

        upload2 = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", file_bytes, "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        assert upload2.status_code == 200
        body2 = upload2.json()
        assert body2["code"] == 1000
        assert body2["result"]["url"].startswith("https://sharepoint.test/share/")
        supply2_id = body2["result"]["supplyId"]

        dup_res = await client.post(
            "/api/v1/supply/get_all_duplicate_resumes",
            json={"supplyId": supply2_id},
            headers={"Authorization": token},
        )
        assert dup_res.status_code == 200
        dup_body = dup_res.json()
        assert dup_body["code"] == 1000
        dups = dup_body["result"]["duplicateResumes"]
        assert any(item["id"] == supply1_id for item in dups)


@pytest.mark.anyio
async def test_supply_match_start_creates_case_and_status_change(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, app)

        vendor_res = await client.post(
            "/api/v1/rk/vendor/add",
            json={"name": "Vendor B", "code": "V002"},
            headers={"Authorization": token},
        )
        vendor_id = vendor_res.json()["result"]["id"]

        upload = await client.post(
            "/api/v1/supply/upload",
            files={"file": ("resume.pdf", b"resume v1", "application/pdf")},
            data={"vendor_id": str(vendor_id), "user_id": "1"},
            headers={"Authorization": token},
        )
        supply_id = upload.json()["result"]["supplyId"]

        # Seed a demand row directly (no public demand CRUD yet)
        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_demand import RkDemand

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            demand = RkDemand(
                name="Demand 1",
                code="D001",
                created_by=1,
                updated_by=1,
                owner_id=1,
                active=True,
                version=1,
            )
            session.add(demand)
            await session.flush()
            demand_id = int(demand.id)
            await session.commit()

        match_res = await client.post(
            "/api/v1/supply/match_start",
            json={
                "demandId": demand_id,
                "supplyIds": [supply_id],
                "roleList": [],
                "flagData": [],
            },
            headers={"Authorization": token},
        )
        assert match_res.status_code == 200
        assert match_res.json()["code"] == 1000

        from sqlalchemy import select

        from backend.app.db.session import get_async_sessionmaker
        from backend.app.models.rk_supply_demand_link import RkSupplyDemandLink

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            existing_case = (
                await session.execute(
                    select(RkSupplyDemandLink).where(
                        RkSupplyDemandLink.demand_id == demand_id,
                        RkSupplyDemandLink.supply_id == supply_id,
                    )
                )
            ).scalar_one_or_none()
            assert existing_case is None

        callback = await client.post(
            "/api/v1/resume/analyze/callback",
            json={
                "eventType": "match",
                "extUniqueId": demand_id,
                "analysis": {
                    "roleList": {"role-a": 1},
                    "thirdPartyAllData": {
                        "role-a": [
                            {
                                "id": supply_id,
                                "score": 88,
                                "conditionMsg": [],
                                "version": 1,
                                "yearsData": {},
                            }
                        ]
                    },
                },
                "extraData": {"demandVersion": 1},
                "llmRaws": [],
            },
        )
        assert callback.status_code == 200
        assert callback.json()["code"] == 1000

        # Load created case
        from backend.app.models.rk_case_status import RkCaseStatus
        from backend.app.models.rk_supply import RkSupply

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            case = (
                await session.execute(
                    select(RkSupplyDemandLink).where(
                        RkSupplyDemandLink.demand_id == demand_id,
                        RkSupplyDemandLink.supply_id == supply_id,
                    )
                )
            ).scalar_one()
            assert case.supply_demand_status3 == "待确认"
            case_id = int(case.id)

        check = await client.post(
            "/api/v1/supply/case_change_status_check",
            json={"caseId": case_id, "beforeStatus": "待确认", "afterStatus": "提案可否确认"},
            headers={"Authorization": token},
        )
        assert check.status_code == 200
        check_body = check.json()
        assert check_body["code"] == 1000
        assert check_body["result"]["allowed"] is True

        change = await client.post(
            "/api/v1/supply/case_change_status",
            json={
                "caseId": case_id,
                "beforeStatus": "待确认",
                "afterStatus": "提案可否确认",
                "userId": 1,
            },
            headers={"Authorization": token},
        )
        assert change.status_code == 200
        change_body = change.json()
        assert change_body["code"] == 1000
        assert change_body["result"]["insertId"] > 0

        async_session = get_async_sessionmaker()
        async with async_session() as session:
            case = (
                await session.execute(select(RkSupplyDemandLink).where(RkSupplyDemandLink.id == case_id))
            ).scalar_one()
            assert case.supply_demand_status3 == "提案可否确认"

            history = (
                await session.execute(select(RkCaseStatus).where(RkCaseStatus.case_id == case_id).order_by(RkCaseStatus.id))
            ).scalars().all()
            assert history[-1].status == "提案可否确认"

            supply = (
                await session.execute(select(RkSupply).where(RkSupply.id == supply_id))
            ).scalar_one()
            assert supply.case_status == "提案可否确认"

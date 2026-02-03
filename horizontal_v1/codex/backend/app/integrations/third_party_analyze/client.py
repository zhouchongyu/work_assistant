from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from backend.app.core.request_id import get_request_id
from backend.app.core.settings import get_settings

logger = logging.getLogger(__name__)


class ThirdPartyAnalyzeClient:
    def __init__(self, *, base_url: str, callback_url: str, timeout_seconds: float = 30.0):
        self._base_url = base_url.rstrip("/")
        self._callback_url = callback_url
        self._timeout_seconds = timeout_seconds

    async def analyze_resume(
        self,
        *,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        supply_id: int,
        version: int,
    ) -> str | None:
        files = {
            "resume_file": (
                filename,
                file_content,
                content_type or "application/octet-stream",
            )
        }
        data = {
            "ext_unique_id": supply_id,
            "callback_url": self._callback_url,
            "extra_data": json.dumps({"version": version}),
        }
        return await self._post_multipart("/v1/third_party/resume/analyze", data=data, files=files)

    async def analyze_resume_proposal(self, *, proposal_document: str, supply_id: int) -> str | None:
        payload = {
            "proposal_document": proposal_document,
            "ext_unique_id": supply_id,
            "callback_url": self._callback_url,
        }
        return await self._post_json("/v1/third_party/resume_proposal/analyze", payload)

    async def analyze_demand_txt(self, *, demand_txt: str, demand_id: int, version: int) -> str | None:
        payload = {
            "demand_txt": demand_txt,
            "ext_unique_id": demand_id,
            "callback_url": self._callback_url,
            "extra_data": {"version": version},
        }
        return await self._post_json("/v1/third_party/demand/analyze", payload)

    async def analyze_match(self, *, demand_id: int, all_data: dict, extra_data: dict) -> str | None:
        payload = {
            "all_data": all_data,
            "ext_unique_id": str(demand_id),
            "callback_url": self._callback_url,
            "extra_data": extra_data,
        }
        return await self._post_json("/v1/third_party/match/analyze", payload)

    async def analyze_similar(self, *, exp_text_a: str, exp_text_b: str) -> dict[str, Any] | None:
        payload = {"exp_text_a": exp_text_a, "exp_text_b": exp_text_b}
        res = await self._post_json("/v1/third_party/resume_similar/analyze", payload, expect_request_id=False)
        if isinstance(res, dict) and "result" in res:
            return res.get("result") or {}
        if isinstance(res, dict):
            return res
        return None

    async def hard_condition(self, *, demand_info: dict, supply_info: dict) -> dict[str, Any] | None:
        payload = {"demand_info": demand_info, "supply_info": supply_info}
        res = await self._post_json("/v1/third_party/hard_condition/analyze", payload, expect_request_id=False)
        if isinstance(res, dict) and "result" in res:
            return res.get("result") or {}
        if isinstance(res, dict):
            return res
        return None

    async def _post_json(self, path: str, payload: dict, *, expect_request_id: bool = True):
        url = f"{self._base_url}{path}"
        headers = {"x-request-id": get_request_id()}
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        if not expect_request_id:
            return data
        if isinstance(data, dict):
            return data.get("request_id")
        return None

    async def _post_multipart(self, path: str, *, data: dict, files: dict):
        url = f"{self._base_url}{path}"
        headers = {"x-request-id": get_request_id()}
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            resp = await client.post(url, data=data, files=files, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
        if isinstance(payload, dict):
            return payload.get("request_id")
        return None


def get_third_party_analyze_client() -> ThirdPartyAnalyzeClient:
    settings = get_settings()
    return ThirdPartyAnalyzeClient(
        base_url=settings.third_party_analyze_url,
        callback_url=settings.callback_base_url,
        timeout_seconds=settings.third_party_timeout_seconds,
    )

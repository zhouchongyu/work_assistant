"""
Third-party AI service client.

Implements request-callback pattern for async AI analysis.

Reference:
- assistant_py/app/v1/service/third_party_client.py
- Wiki: AI机器学习集成/AI机器学习集成.md
"""

import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("work_assistant.ai.client")


class ThirdPartyResumeClient:
    """
    Client for third-party resume analysis service.

    Uses request-callback model:
    1. Submit analysis request with callback_url
    2. Receive request_id immediately
    3. Callback is called when analysis completes
    """

    def __init__(
        self,
        base_url: str | None = None,
        callback_base_url: str | None = None,
    ) -> None:
        self._base_url = (base_url or settings.ai.third_party_analyze_url or "").rstrip("/")
        self._callback_base_url = (
            callback_base_url or settings.ai.callback_base_url or ""
        ).rstrip("/")

    async def analyze_resume(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        supply_id: int,
        version: int,
        timeout: float = 30.0,
    ) -> str | None:
        """
        Submit resume for analysis.

        Args:
            file_content: Resume file content
            filename: Original filename
            content_type: MIME type
            supply_id: Supply ID for callback reference
            version: Supply version
            timeout: Request timeout

        Returns:
            Request ID if successful, None otherwise
        """
        files = {
            "resume_file": (
                filename,
                file_content,
                content_type or "application/octet-stream",
            ),
        }
        data = {
            "ext_unique_id": supply_id,
            "callback_url": f"{self._callback_base_url}/api/v1/resume/analyze/callback",
            "extra_data": json.dumps({"version": version}),
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/resume/analyze",
                    data=data,
                    files=files,
                )
                resp.raise_for_status()
                request_id = resp.json().get("request_id")
                logger.info(
                    f"Resume analysis submitted: supply_id={supply_id}, request_id={request_id}"
                )
                return request_id
        except Exception as e:
            logger.error(f"Failed to submit resume analysis: {e}")
            return None

    async def analyze_resume_proposal(
        self,
        proposal_document: str,
        supply_id: int,
        timeout: float = 30.0,
    ) -> str | None:
        """
        Submit resume proposal document for analysis.

        Args:
            proposal_document: Proposal document text
            supply_id: Supply ID
            timeout: Request timeout

        Returns:
            Request ID if successful
        """
        data = {
            "proposal_document": proposal_document,
            "ext_unique_id": supply_id,
            "callback_url": f"{self._callback_base_url}/api/v1/resume/analyze/callback",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/resume_proposal/analyze",
                    json=data,
                )
                resp.raise_for_status()
                return resp.json().get("request_id")
        except Exception as e:
            logger.error(f"Failed to submit proposal analysis: {e}")
            return None

    async def analyze_demand(
        self,
        demand_txt: str,
        demand_id: int,
        version: int,
        timeout: float = 30.0,
    ) -> str | None:
        """
        Submit demand text for analysis.

        Args:
            demand_txt: Demand description text
            demand_id: Demand ID
            version: Demand version
            timeout: Request timeout

        Returns:
            Request ID if successful
        """
        data = {
            "demand_txt": demand_txt,
            "ext_unique_id": demand_id,
            "callback_url": f"{self._callback_base_url}/api/v1/resume/analyze/callback",
            "extra_data": {"version": version},
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/demand/analyze",
                    json=data,
                )
                resp.raise_for_status()
                logger.info(
                    f"Demand analysis submitted: demand_id={demand_id}"
                )
                return resp.json().get("request_id")
        except Exception as e:
            logger.error(f"Failed to submit demand analysis: {e}")
            return None

    async def analyze_match(
        self,
        demand_id: int,
        all_data: dict[str, Any],
        extra_data: dict[str, Any],
        timeout: float = 30.0,
    ) -> str | None:
        """
        Submit match analysis request.

        Args:
            demand_id: Demand ID
            all_data: Complete data for matching
            extra_data: Additional metadata
            timeout: Request timeout

        Returns:
            Request ID if successful
        """
        data = {
            "all_data": all_data,
            "ext_unique_id": str(demand_id),
            "callback_url": f"{self._callback_base_url}/api/v1/resume/analyze/callback",
            "extra_data": extra_data,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/match/analyze",
                    json=data,
                )
                resp.raise_for_status()
                logger.info(f"Match analysis submitted: demand_id={demand_id}")
                return resp.json().get("request_id")
        except Exception as e:
            logger.error(f"Failed to submit match analysis: {e}")
            return None

    async def analyze_similar(
        self,
        exp_text_a: str,
        exp_text_b: str,
        timeout: float = 30.0,
    ) -> dict[str, Any] | None:
        """
        Analyze similarity between two experience texts.

        This is a synchronous call (returns result immediately).

        Args:
            exp_text_a: First experience text
            exp_text_b: Second experience text
            timeout: Request timeout

        Returns:
            Similarity analysis result
        """
        data = {
            "exp_text_a": exp_text_a,
            "exp_text_b": exp_text_b,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/resume_similar/analyze",
                    json=data,
                )
                resp.raise_for_status()
                payload = resp.json()
                if isinstance(payload, dict) and "result" in payload:
                    return payload.get("result") or {}
                return payload or {}
        except Exception as e:
            logger.error(f"Failed to analyze similarity: {e}")
            return None

    async def get_hard_condition(
        self,
        demand_info: dict[str, Any],
        supply_info: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any] | None:
        """
        Get hard condition matching result.

        This is a synchronous call (returns result immediately).

        Args:
            demand_info: Demand information
            supply_info: Supply information
            timeout: Request timeout

        Returns:
            Hard condition analysis result
        """
        data = {
            "demand_info": demand_info,
            "supply_info": supply_info,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/third_party/hard_condition/analyze",
                    json=data,
                )
                resp.raise_for_status()
                return resp.json().get("result") or {}
        except Exception as e:
            logger.error(f"Failed to get hard condition: {e}")
            return None


# Singleton instance
third_party_client = ThirdPartyResumeClient()

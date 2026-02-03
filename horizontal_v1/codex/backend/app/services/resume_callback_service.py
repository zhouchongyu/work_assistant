from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.rk_demand import RkDemand
from backend.app.models.rk_llm_data import RkLlmData
from backend.app.models.rk_match_res import RkMatchRes
from backend.app.models.rk_supply import RkSupply
from backend.app.models.rk_supply_ai import RkSupplyAi
from backend.app.models.rk_supply_demand_link import RkSupplyDemandLink


def _get_any(d: dict, *keys: str, default=None):
    for k in keys:
        if k in d:
            return d.get(k)
    return default


def _as_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _as_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "y", "on"}
    return False


def _extract_role_limits(role_list: Any) -> dict[str, int]:
    if isinstance(role_list, dict):
        return {str(k): int(v or 0) for k, v in role_list.items()}

    if isinstance(role_list, list):
        limits: dict[str, int] = {}
        for item in role_list:
            if not isinstance(item, dict):
                continue
            name = _get_any(item, "label", "role", "name")
            amount = _get_any(item, "amount", "num", "limit", "count")
            if name is None:
                continue
            limits[str(name)] = int(amount or 0)
        return limits

    return {}


def _extract_warning_msgs(condition_msg: Any) -> list[str]:
    if not condition_msg:
        return []
    if isinstance(condition_msg, list):
        out: list[str] = []
        for item in condition_msg:
            if isinstance(item, str):
                out.append(item)
                continue
            if isinstance(item, dict):
                zh = item.get("zh")
                if isinstance(zh, str) and zh:
                    out.append(zh)
        return out
    return []


async def process_resume_callback_payload(payload: dict, session: AsyncSession) -> None:
    event_type = _get_any(payload, "event_type", "eventType")
    if not isinstance(event_type, str) or not event_type:
        return

    analysis = _get_any(payload, "analysis") or {}
    if not isinstance(analysis, dict):
        analysis = {}

    extra_data = _get_any(payload, "extra_data", "extraData") or {}
    if not isinstance(extra_data, dict):
        extra_data = {}

    version_tag = _get_any(payload, "version_tag", "versionTag") or ""
    ext_unique_id = _get_any(payload, "ext_unique_id", "extUniqueId")

    stop_err = _as_bool(_get_any(analysis, "stop_err", "stopErr"))

    supply_id_ctx: int | None = None
    demand_id_ctx: int | None = None
    supply_version: int | None = None
    demand_version: int | None = None

    version = _as_int(_get_any(extra_data, "version"))
    if version is not None and event_type == "resume":
        supply_version = version
    if version is not None and event_type == "demand":
        demand_version = version

    if event_type in {"resume", "resume_contact"}:
        supply_id_ctx = _as_int(ext_unique_id)
    elif event_type in {"demand", "match"}:
        demand_id_ctx = _as_int(ext_unique_id)

    # Persist raw LLM outputs (best-effort).
    llm_raws = _get_any(payload, "llm_raws", "llmRaws") or []
    if isinstance(llm_raws, list):
        for raw in llm_raws:
            if not isinstance(raw, dict):
                continue
            session.add(
                RkLlmData(
                    demand_id=demand_id_ctx,
                    supply_id=supply_id_ctx,
                    event_type=_get_any(raw, "event_type", "eventType"),
                    res=_get_any(raw, "res"),
                    model=_get_any(raw, "model"),
                    special=_get_any(raw, "special"),
                    parent_id=_as_int(_get_any(raw, "parent_id", "parentId")),
                    third_id=_as_int(_get_any(raw, "third_id", "thirdId")),
                    context=_get_any(raw, "context"),
                    demand_version=demand_version,
                    supply_version=supply_version,
                )
            )

    if event_type in {"resume", "resume_contact"}:
        supply_id = supply_id_ctx
        if not supply_id:
            return
        supply = (await session.execute(select(RkSupply).where(RkSupply.id == supply_id))).scalar_one_or_none()
        if not supply:
            return

        supply.analysis_version = str(version_tag or supply.analysis_version or "")
        if event_type == "resume":
            supply.analysis_status = "analysis_error" if stop_err else "analysis_done"
            # Minimal v1: persist the raw analysis payload for later drill-down.
            supply_ai = (
                await session.execute(select(RkSupplyAi).where(RkSupplyAi.supply_id == supply_id))
            ).scalar_one_or_none()
            if not supply_ai:
                supply_ai = RkSupplyAi(supply_id=supply_id)
                session.add(supply_ai)
            supply_ai.basic = analysis
        else:
            supply.contact_analysis_status = "contact_analysis_error" if stop_err else "contact_analysis_done"
        await session.flush()
        return

    if event_type == "demand":
        demand_id = demand_id_ctx
        if not demand_id:
            return
        demand = (await session.execute(select(RkDemand).where(RkDemand.id == demand_id))).scalar_one_or_none()
        if not demand:
            return
        demand.analysis_status = "analysis_error" if stop_err else "analysis_done"
        await session.flush()
        return

    if event_type == "match":
        demand_id = demand_id_ctx
        if not demand_id:
            return

        demand = (await session.execute(select(RkDemand).where(RkDemand.id == demand_id))).scalar_one_or_none()
        if not demand:
            return

        demand_version = _as_int(_get_any(extra_data, "demand_version", "demandVersion")) or int(demand.version or 1)
        if stop_err:
            demand.analysis_status = "match_error"
            await session.flush()
            return

        third_party_all_data = _get_any(analysis, "third_party_all_data", "thirdPartyAllData") or {}
        if not isinstance(third_party_all_data, dict):
            third_party_all_data = {}
        role_limits = _extract_role_limits(_get_any(analysis, "role_list", "roleList"))

        supply_trigger = _as_int(_get_any(extra_data, "supply_trigger", "supplyTrigger"))
        if not supply_trigger:
            await session.execute(
                delete(RkSupplyDemandLink).where(
                    RkSupplyDemandLink.demand_id == demand_id,
                    RkSupplyDemandLink.demand_version == demand_version,
                )
            )
            await session.execute(
                delete(RkMatchRes).where(
                    RkMatchRes.demand_id == demand_id,
                    RkMatchRes.demand_version == demand_version,
                )
            )

        for role_name, role_data in third_party_all_data.items():
            if not isinstance(role_data, list):
                continue

            candidates: list[dict[str, Any]] = []
            for one in role_data:
                if not isinstance(one, dict):
                    continue
                supply_id = _as_int(_get_any(one, "id"))
                if not supply_id:
                    continue
                score = float(_get_any(one, "score") or 0)
                supply_version = _as_int(_get_any(one, "version")) or 0
                years_data = _get_any(one, "years_data", "yearsData") or {}
                condition_msg = _get_any(one, "condition_msg", "conditionMsg") or []

                warning_msgs = _extract_warning_msgs(condition_msg)
                candidates.append(
                    {
                        "supply_id": supply_id,
                        "score": score,
                        "supply_version": supply_version,
                        "warning_msg": warning_msgs,
                    }
                )

                existing = (
                    await session.execute(
                        select(RkMatchRes).where(
                            RkMatchRes.demand_id == demand_id,
                            RkMatchRes.supply_id == supply_id,
                            RkMatchRes.demand_role == str(role_name),
                            RkMatchRes.demand_version == demand_version,
                        )
                    )
                ).scalar_one_or_none()
                if existing:
                    existing.score = score
                    existing.warning_msg = warning_msgs
                    existing.years_data = years_data
                    existing.supply_version = supply_version
                else:
                    session.add(
                        RkMatchRes(
                            demand_id=demand_id,
                            supply_id=supply_id,
                            demand_role=str(role_name),
                            score=score,
                            warning_msg=warning_msgs,
                            years_data=years_data,
                            demand_version=demand_version,
                            supply_version=supply_version,
                            type="",
                            msg=[],
                            created_by=demand.owner_id,
                            updated_by=demand.owner_id,
                            owner_id=demand.owner_id,
                            department_id=demand.department_id,
                            active=True,
                            to_be_confirmed=False,
                        )
                    )

            limit_num = int(role_limits.get(str(role_name)) or 0)
            if limit_num <= 0:
                continue

            sorted_candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit_num]
            for c in sorted_candidates:
                supply_id = int(c["supply_id"])
                existing_case = (
                    await session.execute(
                        select(RkSupplyDemandLink).where(
                            RkSupplyDemandLink.demand_id == demand_id,
                            RkSupplyDemandLink.supply_id == supply_id,
                            RkSupplyDemandLink.demand_role == str(role_name),
                            RkSupplyDemandLink.demand_version == demand_version,
                        )
                    )
                ).scalar_one_or_none()
                if existing_case:
                    existing_case.score = c["score"]
                    existing_case.warning_msg = c["warning_msg"]
                    existing_case.supply_version = c["supply_version"]
                else:
                    session.add(
                        RkSupplyDemandLink(
                            demand_id=demand_id,
                            supply_id=supply_id,
                            supply_demand_status3="待确认",
                            supply_demand_status5="自动匹配",
                            score=c["score"],
                            warning_msg=c["warning_msg"],
                            demand_role=str(role_name),
                            demand_version=demand_version,
                            supply_version=c["supply_version"],
                            created_by=demand.owner_id,
                            updated_by=demand.owner_id,
                            owner_id=demand.owner_id,
                            department_id=demand.department_id,
                            active=True,
                            to_be_confirmed=False,
                        )
                    )

        demand.have_match = True
        demand.analysis_status = "match_done"
        await session.flush()
        return

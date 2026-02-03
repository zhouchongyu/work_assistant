from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.rk_case_status import RkCaseStatus
from backend.app.models.rk_supply import RkSupply
from backend.app.models.rk_supply_demand_link import RkSupplyDemandLink


class CaseServiceError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


CASE_STATUS_LEVEL: dict[str, int] = {
    "待确认": 1,
    "提案可否确认": 2,
    "提案济": 3,
    "1/2提案济": 4,
    "1/3提案济": 5,
    "面试调整中": 6,
    "1/2面试调整中": 7,
    "1/3面试调整中": 8,
    "面试设定济": 9,
    "1/2面试设定济": 10,
    "1/3面试设定济": 11,
    "结果等待": 12,
    "1/2结果等待": 13,
    "1/3结果等待": 14,
    "2/2提案济": 15,
    "2/3提案济": 16,
    "2/2面试调整中": 17,
    "2/3面试调整中": 18,
    "2/2面试设定济": 19,
    "2/3面试设定济": 20,
    "2/2结果等待": 21,
    "2/3结果等待": 22,
    "3/3提案济": 23,
    "3/3面试调整中": 24,
    "3/3面试设定济": 25,
    "3/3结果等待": 26,
    "条件交涉": 27,
    "受注": 28,
    "入場処理": 29,
    "情况确认": 30,
    "退場処理": 31,
}

CASE_TIAOJIAN_LEVEL = 27
CASE_SHOUZHU_LEVEL = 28
CASE_MAX_INTERVIEW = 26
CASE_INIT_LEVEL = 1

INTERVIEW_STAGE_SUFFIX = {
    "提案济": "proposal",
    "面试调整中": "adjust",
    "面试设定济": "setup",
    "结果等待": "waiting",
}

ROUND_TAGS: dict[str, tuple[int, int]] = {
    "": (1, 1),
    "1/2": (1, 2),
    "1/3": (1, 3),
    "2/2": (2, 2),
    "2/3": (2, 3),
    "3/3": (3, 3),
}

STAGE_ORDER = {"proposal": 0, "adjust": 1, "setup": 2, "waiting": 3}

CASE_STATUS_META: dict[str, dict[str, int | str | None]] = {}
for prefix, (round_idx, total_round) in ROUND_TAGS.items():
    for suffix, stage in INTERVIEW_STAGE_SUFFIX.items():
        status_name = f"{prefix}{suffix}"
        if status_name in CASE_STATUS_LEVEL:
            CASE_STATUS_META[status_name] = {
                "stage": stage,
                "round": round_idx,
                "total": total_round,
            }

FIRST_ROUND_PROPOSALS = [
    k for k, v in CASE_STATUS_META.items() if v.get("stage") == "proposal" and v.get("round") == 1
]
FIRST_ROUND_ADJUSTS = [
    k for k, v in CASE_STATUS_META.items() if v.get("stage") == "adjust" and v.get("round") == 1
]
FIRST_ROUND_SETUPS = [
    k for k, v in CASE_STATUS_META.items() if v.get("stage") == "setup" and v.get("round") == 1
]
FIRST_ROUND_WAITINGS = [
    k for k, v in CASE_STATUS_META.items() if v.get("stage") == "waiting" and v.get("round") == 1
]
ALL_PROPOSALS = [k for k, v in CASE_STATUS_META.items() if v.get("stage") == "proposal"]

NO_ROLLBACK_LEVEL = CASE_STATUS_LEVEL.get("入場処理", 10**6)


@dataclass(frozen=True)
class CaseStatusCheckResult:
    allowed: bool
    reason: str
    suggestions: list[str]


class CaseService:
    @staticmethod
    def _get_status_meta(status: str) -> dict[str, int | str | None]:
        return CASE_STATUS_META.get(status, {"stage": "other", "round": None, "total": None})

    @staticmethod
    def _status_by_round_stage(round_idx: int, total_round: int, stage: str) -> str | None:
        for name, meta in CASE_STATUS_META.items():
            if meta.get("round") == round_idx and meta.get("total") == total_round and meta.get("stage") == stage:
                return name
        return None

    @staticmethod
    def _proposal_statuses_for_total(total_round: int | None) -> list[str]:
        if not total_round:
            return []
        return [
            name
            for name, meta in CASE_STATUS_META.items()
            if meta.get("stage") == "proposal" and meta.get("total") == total_round
        ]

    @staticmethod
    def _has_round_proposal(
        history_statuses: Sequence[str], round_idx: int | None, total_round: int | None
    ) -> bool:
        if not round_idx:
            return True
        for status in history_statuses:
            meta = CASE_STATUS_META.get(status)
            if not meta:
                continue
            if meta.get("stage") != "proposal":
                continue
            if meta.get("round") != round_idx:
                continue
            if not total_round or meta.get("total") == total_round:
                return True
            return True
        return False

    @staticmethod
    def _max_total_round(history_statuses: Sequence[str]) -> int:
        max_total = 1
        for status in history_statuses:
            meta = CASE_STATUS_META.get(status)
            if not meta:
                continue
            total = meta.get("total")
            if total:
                max_total = max(max_total, int(total))
        return max_total

    @classmethod
    async def _rewrite_chain_prefix(
        cls,
        active_records: list[RkCaseStatus],
        target_round: int | None,
        target_total: int | None,
        max_stage_order: int,
        session: AsyncSession,
    ) -> None:
        if not target_round or not target_total:
            return
        last_proposal = None
        for rec in reversed(active_records):
            if cls._get_status_meta(rec.status).get("stage") == "proposal":
                last_proposal = rec
                break
        if not last_proposal:
            return
        chain_records = [
            r
            for r in active_records
            if r.id >= last_proposal.id and cls._get_status_meta(r.status).get("stage") in STAGE_ORDER
        ]
        for rec in chain_records:
            stage = cls._get_status_meta(rec.status).get("stage")
            if stage not in STAGE_ORDER:
                continue
            if STAGE_ORDER[stage] > max_stage_order:
                continue
            new_status = cls._status_by_round_stage(int(target_round), int(target_total), str(stage))
            if new_status and new_status != rec.status:
                rec.status = new_status
        await session.flush()

    @classmethod
    async def _rewrite_all_rounds(
        cls, active_records: list[RkCaseStatus], target_total: int, session: AsyncSession
    ) -> None:
        if not target_total:
            return
        proposal_idx = 0
        for rec in active_records:
            meta = cls._get_status_meta(rec.status)
            if meta.get("stage") == "proposal":
                proposal_idx += 1
            if meta.get("stage") not in STAGE_ORDER:
                continue
            if proposal_idx == 0:
                continue
            new_status = cls._status_by_round_stage(proposal_idx, target_total, str(meta.get("stage")))
            if new_status and new_status != rec.status:
                rec.status = new_status
        await session.flush()

    @classmethod
    def _allowed_forward_statuses(cls, current_status: str) -> set[str]:
        allowed: set[str] = set()
        meta = cls._get_status_meta(current_status)

        if current_status == "待确认":
            allowed.add("提案可否确认")
        if current_status == "提案可否确认":
            allowed.update(FIRST_ROUND_PROPOSALS)

        if meta.get("stage") == "proposal":
            if meta.get("round") == 1:
                allowed.update(FIRST_ROUND_ADJUSTS)
            else:
                next_status = cls._status_by_round_stage(int(meta.get("round") or 0), int(meta.get("total") or 0), "adjust")
                if next_status:
                    allowed.add(next_status)
        elif meta.get("stage") == "adjust":
            if meta.get("round") == 1:
                allowed.update(FIRST_ROUND_SETUPS)
            else:
                next_status = cls._status_by_round_stage(int(meta.get("round") or 0), int(meta.get("total") or 0), "setup")
                if next_status:
                    allowed.add(next_status)
        elif meta.get("stage") == "setup":
            if meta.get("round") == 1:
                allowed.update(FIRST_ROUND_WAITINGS)
            else:
                next_status = cls._status_by_round_stage(int(meta.get("round") or 0), int(meta.get("total") or 0), "waiting")
                if next_status:
                    allowed.add(next_status)
        elif meta.get("stage") == "waiting":
            round_idx = meta.get("round")
            total_round = meta.get("total")
            if round_idx and total_round and int(round_idx) < int(total_round):
                next_status = cls._status_by_round_stage(int(round_idx) + 1, int(total_round), "proposal")
                if next_status:
                    allowed.add(next_status)
            allowed.add("条件交涉")
            allowed.update(ALL_PROPOSALS)

        if current_status == "条件交涉":
            allowed.update({"受注"})
            allowed.update(ALL_PROPOSALS)
        if current_status == "受注":
            allowed.update({"入場処理"})
            allowed.update(ALL_PROPOSALS)
        if current_status == "入場処理":
            allowed.add("情况确认")
        if current_status == "情况确认":
            allowed.add("退場処理")

        return allowed

    @classmethod
    async def _has_order_conflict(cls, case_obj: RkSupplyDemandLink, session: AsyncSession) -> bool:
        result = await session.execute(
            select(RkSupplyDemandLink).where(
                RkSupplyDemandLink.supply_id == case_obj.supply_id, RkSupplyDemandLink.active.is_(True)
            )
        )
        all_cases = result.scalars().all()
        for other in all_cases:
            if other.id == case_obj.id:
                continue
            tmp_level = CASE_STATUS_LEVEL.get(other.supply_demand_status3 or "") or 0
            if tmp_level >= CASE_SHOUZHU_LEVEL:
                return True
        return False

    @classmethod
    async def _validate_change(
        cls,
        case_obj: RkSupplyDemandLink,
        before_status: str,
        after_status: str,
        history_statuses: list[str],
        session: AsyncSession,
    ) -> CaseStatusCheckResult:
        suggestions: set[str] = set()

        before_level = CASE_STATUS_LEVEL.get(before_status) or 0
        after_level = CASE_STATUS_LEVEL.get(after_status) or 0
        before_meta = cls._get_status_meta(before_status)
        after_meta = cls._get_status_meta(after_status)

        if after_status == before_status:
            return CaseStatusCheckResult(True, "状态未变更", [])

        if before_level >= NO_ROLLBACK_LEVEL and after_level < before_level:
            return CaseStatusCheckResult(False, "入場処理及以上不允许回滚", [])

        if after_status == "受注":
            if await cls._has_order_conflict(case_obj, session):
                return CaseStatusCheckResult(False, "同简历下已有有效case处于受注及以上，不能再设为受注", [])

        if (
            after_meta.get("stage") in {"adjust", "setup", "waiting"}
            and after_meta.get("round")
            and int(after_meta.get("round") or 0) > 1
        ):
            if not cls._has_round_proposal(
                history_statuses, int(after_meta.get("round") or 0), int(after_meta.get("total") or 0)
            ):
                suggestions.update(cls._proposal_statuses_for_total(int(after_meta.get("total") or 0)))
                return CaseStatusCheckResult(False, f"{after_status} 需要先出现对应轮次的提案状态", sorted(suggestions))

        if (
            after_meta.get("stage") in STAGE_ORDER
            and before_meta.get("stage") == after_meta.get("stage")
            and after_meta.get("round") == before_meta.get("round")
            and after_meta.get("total")
            and before_meta.get("total")
            and after_meta.get("total") != before_meta.get("total")
        ):
            return CaseStatusCheckResult(True, "允许调整轮次总数", [])

        forward_options = cls._allowed_forward_statuses(before_status)
        if after_level > before_level:
            if after_status not in forward_options:
                suggestions.update(forward_options)
                if forward_options:
                    readable = "、".join(sorted(forward_options))
                    return CaseStatusCheckResult(False, f"{before_status} 之后仅可变更为: {readable}", sorted(suggestions))
                return CaseStatusCheckResult(False, "当前状态无法推进", [])
            return CaseStatusCheckResult(True, "允许变更", [])

        if after_level < before_level:
            return CaseStatusCheckResult(True, "允许回滚", [])

        return CaseStatusCheckResult(False, "状态变更不合法", [])

    @classmethod
    async def _list_history(
        cls, session: AsyncSession, *, case_id: int, active: bool | None
    ) -> list[RkCaseStatus]:
        q = select(RkCaseStatus).where(RkCaseStatus.case_id == case_id).order_by(RkCaseStatus.id)
        if active is not None:
            q = q.where(RkCaseStatus.active.is_(active))
        return (await session.execute(q)).scalars().all()

    @classmethod
    async def _insert_status(
        cls, session: AsyncSession, *, case_id: int, status: str, remark: str | None = ""
    ) -> RkCaseStatus:
        record = RkCaseStatus(case_id=case_id, status=status, remark=remark or "", active=True)
        session.add(record)
        await session.flush()
        return record

    @classmethod
    async def _update_case_status_history(
        cls, session: AsyncSession, *, case_id: int, before_status: str, after_status: str
    ) -> int:
        insert_id = 0
        history_records = await cls._list_history(session, case_id=case_id, active=None)
        active_records = [rec for rec in history_records if rec.active]

        after_meta = cls._get_status_meta(after_status)
        after_level = CASE_STATUS_LEVEL.get(after_status) or 0
        before_level = CASE_STATUS_LEVEL.get(before_status) or 0
        is_rollback = after_level < before_level
        is_restart = after_meta.get("stage") == "proposal" and before_level >= CASE_SHOUZHU_LEVEL

        current_total = cls._max_total_round([rec.status for rec in active_records if rec.status]) if active_records else 1
        target_total_for_all = after_meta.get("total")
        if target_total_for_all and int(target_total_for_all) != current_total:
            await cls._rewrite_all_rounds(active_records, int(target_total_for_all), session)
            history_records = await cls._list_history(session, case_id=case_id, active=None)
            active_records = [rec for rec in history_records if rec.active]

        before_meta = cls._get_status_meta(before_status)
        if (
            after_meta.get("stage") in STAGE_ORDER
            and before_meta.get("stage") == after_meta.get("stage")
            and after_meta.get("round") == before_meta.get("round")
        ):
            target_stage = after_meta.get("stage")
            target_round = after_meta.get("round")
            target_total = int(after_meta.get("total") or before_meta.get("total") or 1)

            if target_total != int(before_meta.get("total") or 1):
                await cls._rewrite_all_rounds(active_records, target_total, session)
                history_records = await cls._list_history(session, case_id=case_id, active=None)
                active_records = [rec for rec in history_records if rec.active]

            last_match = None
            for rec in reversed(active_records):
                meta = cls._get_status_meta(rec.status)
                if meta.get("stage") == target_stage and meta.get("round") == target_round:
                    last_match = rec
                    break
            if not last_match:
                last_match = active_records[-1] if active_records else None
            if last_match:
                last_match.status = after_status
                await session.flush()
            else:
                insert_res = await cls._insert_status(session, case_id=case_id, status=after_status, remark="")
                insert_id = int(insert_res.id)
            return insert_id

        if is_restart and after_meta.get("round") and int(after_meta.get("round") or 0) > 1:
            target_total = int(after_meta.get("total") or 1)
            round_idx = 0
            round_map: dict[int, int] = {}
            for rec in active_records:
                meta = cls._get_status_meta(rec.status)
                if meta.get("stage") == "proposal":
                    round_idx += 1
                round_map[int(rec.id)] = round_idx
            for rec in active_records:
                stage = cls._get_status_meta(rec.status).get("stage")
                if stage in STAGE_ORDER:
                    idx = round_map.get(int(rec.id)) or 0
                    if idx == 0:
                        continue
                    new_status = cls._status_by_round_stage(idx, target_total, str(stage))
                    if new_status and new_status != rec.status:
                        rec.status = new_status
                else:
                    level = CASE_STATUS_LEVEL.get(rec.status) or 0
                    if level > CASE_MAX_INTERVIEW:
                        rec.active = False
            await session.flush()
            insert_res = await cls._insert_status(session, case_id=case_id, status=after_status, remark="")
            return int(insert_res.id)

        if is_rollback:
            def _rollback_level(status: str) -> int:
                meta = cls._get_status_meta(status)
                level = CASE_STATUS_LEVEL.get(status) or 0
                if meta.get("stage") in STAGE_ORDER:
                    target_round = meta.get("round")
                    if target_round:
                        same_round_levels = [
                            CASE_STATUS_LEVEL.get(name) or level
                            for name, m in CASE_STATUS_META.items()
                            if m.get("stage") == meta.get("stage") and m.get("round") == target_round
                        ]
                        if same_round_levels:
                            level = min(same_round_levels)
                return level

            after_level_normalized = _rollback_level(after_status)
            to_inactive = [
                rec
                for rec in active_records
                if _rollback_level(rec.status) >= after_level_normalized
            ]
            for rec in to_inactive:
                rec.active = False
            await session.flush()
            active_records = [
                rec
                for rec in active_records
                if _rollback_level(rec.status) < after_level_normalized and rec.active
            ]

        if after_meta.get("stage") in STAGE_ORDER:
            skip_rewrite = False
            if is_rollback and after_meta.get("round") and int(after_meta.get("round") or 0) > 1:
                skip_rewrite = True
            if (
                (not is_rollback)
                and after_meta.get("stage") == "proposal"
                and after_meta.get("round")
                and int(after_meta.get("round") or 0) > 1
            ):
                exists_same_round = False
                for rec in active_records:
                    meta = cls._get_status_meta(rec.status)
                    if (
                        meta.get("stage") == "proposal"
                        and meta.get("round") == after_meta.get("round")
                        and meta.get("total") == after_meta.get("total")
                    ):
                        exists_same_round = True
                        break
                if not exists_same_round:
                    skip_rewrite = True

            if not skip_rewrite:
                max_stage_order = STAGE_ORDER[str(after_meta.get("stage"))]
                await cls._rewrite_chain_prefix(
                    active_records,
                    int(after_meta.get("round") or 0) or None,
                    int(after_meta.get("total") or 0) or None,
                    max_stage_order,
                    session,
                )

        insert_res = await cls._insert_status(session, case_id=case_id, status=after_status, remark="")
        insert_id = int(insert_res.id)
        return insert_id

    @classmethod
    async def check_case_status_change(
        cls, session: AsyncSession, *, case_id: int | None, before_status: str, after_status: str
    ) -> CaseStatusCheckResult:
        if not case_id:
            if after_status not in ["待确认", "提案可否确认"]:
                return CaseStatusCheckResult(
                    allowed=False,
                    reason="初始状态只能为'待确认'或'提案可否确认'",
                    suggestions=["待确认", "提案可否确认"],
                )
            return CaseStatusCheckResult(True, "", [])

        before_level = CASE_STATUS_LEVEL.get(before_status)
        after_level = CASE_STATUS_LEVEL.get(after_status)
        if not before_level or not after_level:
            raise CaseServiceError("状态不存在")

        case_obj = (
            await session.execute(select(RkSupplyDemandLink).where(RkSupplyDemandLink.id == case_id))
        ).scalar_one_or_none()
        if not case_obj:
            raise CaseServiceError("case不存在")

        current_status = case_obj.supply_demand_status3 or ""
        if current_status and current_status != before_status:
            raise CaseServiceError(f"case当前状态为{current_status}，请刷新后重试")

        history_records = await cls._list_history(session, case_id=int(case_id), active=None)
        history_statuses = [item.status for item in history_records if item.status]
        if current_status:
            history_statuses.append(current_status)

        validated = await cls._validate_change(case_obj, before_status, after_status, history_statuses, session)
        return validated

    @classmethod
    async def change_case_status(
        cls, session: AsyncSession, *, case_id: int, before_status: str, after_status: str
    ) -> dict:
        before_level = CASE_STATUS_LEVEL.get(before_status)
        after_level = CASE_STATUS_LEVEL.get(after_status)
        if not before_level or not after_level:
            raise CaseServiceError("状态不存在")

        msg_list: list[str] = []
        close_case_ids: list[int] = []

        if before_level == after_level:
            return {"insert_id": 0, "msg": "", "close_case_ids": []}

        case_obj = (
            await session.execute(select(RkSupplyDemandLink).where(RkSupplyDemandLink.id == case_id))
        ).scalar_one_or_none()
        if not case_obj:
            raise CaseServiceError("case不存在")

        insert_id = await cls._update_case_status_history(
            session, case_id=case_id, before_status=before_status, after_status=after_status
        )

        # Update current case status on case table (v1 uses supplyDemandStatus3)
        case_obj.supply_demand_status3 = after_status
        await session.flush()

        # Rollback: restore other closed cases
        if before_level >= CASE_SHOUZHU_LEVEL and after_level < CASE_SHOUZHU_LEVEL:
            result = await session.execute(
                select(RkSupplyDemandLink).where(
                    RkSupplyDemandLink.supply_id == case_obj.supply_id, RkSupplyDemandLink.active.is_(False)
                )
            )
            for other in result.scalars().all():
                if other.id == case_obj.id:
                    continue
                tmp_level = CASE_STATUS_LEVEL.get(other.supply_demand_status3 or "") or 0
                if tmp_level > CASE_INIT_LEVEL:
                    other.active = True
                    msg_list.append(f"恢复case: {int(other.id)} 状态: {other.supply_demand_status3} 为有效")

        # 受注: close other cases
        if before_level < CASE_SHOUZHU_LEVEL and after_level >= CASE_SHOUZHU_LEVEL:
            result = await session.execute(
                select(RkSupplyDemandLink).where(
                    RkSupplyDemandLink.supply_id == case_obj.supply_id, RkSupplyDemandLink.active.is_(True)
                )
            )
            for other in result.scalars().all():
                if other.id == case_obj.id:
                    continue
                other.active = False
                other.reason = f"因其他 Case {case_obj.id} 被更新为状态「{after_status}」，现已被自动标记为无效。"
                msg_list.append(f"设置case{int(other.id)}(状态: {other.supply_demand_status3}): 为无效")
                close_case_ids.append(int(other.id))

        # Update supply case_status as max level among active cases
        result = await session.execute(
            select(RkSupplyDemandLink).where(
                RkSupplyDemandLink.supply_id == case_obj.supply_id, RkSupplyDemandLink.active.is_(True)
            )
        )
        max_status_level = 0
        max_status = ""
        for tmp in result.scalars().all():
            tmp_level = CASE_STATUS_LEVEL.get(tmp.supply_demand_status3 or "") or 0
            if tmp_level > max_status_level:
                max_status_level = tmp_level
                max_status = tmp.supply_demand_status3 or ""

        if max_status and case_obj.supply_id:
            supply = (
                await session.execute(select(RkSupply).where(RkSupply.id == case_obj.supply_id))
            ).scalar_one_or_none()
            if supply and supply.case_status != max_status:
                supply.case_status = max_status
                msg_list.append(f"更新简历{int(case_obj.supply_id)}: 内部状态为 「{max_status}」")

        await session.flush()

        return {"insert_id": insert_id, "msg": "\n".join(msg_list), "close_case_ids": close_case_ids}

    @classmethod
    async def case_invalid_batch(
        cls, session: AsyncSession, *, case_ids: list[int], unique_id: int, table_name: str
    ) -> None:
        if table_name not in ["rk_supply", "rk_demand"]:
            raise CaseServiceError("参数错误")
        if not case_ids:
            return

        q = select(RkSupplyDemandLink).where(RkSupplyDemandLink.id.in_(case_ids))
        if table_name == "rk_supply":
            q = q.where(RkSupplyDemandLink.supply_id == unique_id)
        else:
            q = q.where(RkSupplyDemandLink.demand_id == unique_id)
        rows = (await session.execute(q)).scalars().all()
        if len(rows) != len(case_ids):
            raise CaseServiceError("存在不符合条件的case，执行失败")
        for rec in rows:
            rec.active = False
            rec.to_be_confirmed = False
        await session.flush()

    @classmethod
    async def update_case_status_remark(
        cls, session: AsyncSession, *, case_id: int, case_status_id: int, remark_text: str | None
    ) -> None:
        remark_text = remark_text or ""
        if len(remark_text) > 500:
            raise CaseServiceError("备注长度不能超过500字符")
        record = (
            await session.execute(select(RkCaseStatus).where(RkCaseStatus.id == case_status_id))
        ).scalar_one_or_none()
        if not record:
            raise CaseServiceError("状态记录不存在")
        if int(record.case_id) != int(case_id):
            raise CaseServiceError("状态记录不属于当前case")
        record.remark = remark_text
        await session.flush()


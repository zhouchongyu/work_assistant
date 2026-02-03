"""
Demand matching service.

Handles:
- Analyzing demand requirements
- Matching supplies with demands
- Creating case records for matches

Reference:
- assistant_py/resume/case_compare.py
- Wiki: AI机器学习集成/智能匹配算法.md
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_context
from app.mqtt import send_demand_analysis_notification, send_match_complete_notification

logger = logging.getLogger("work_assistant.services.demand_matcher")


async def case_compare_service(
    demand_id: int,
    params: dict[str, Any],
) -> None:
    """
    Match supplies against a demand and create case records.

    This function:
    1. Analyzes demand to extract X/Y/Z skill requirements
    2. Searches for supplies with matching skills
    3. Calculates match scores
    4. Creates case records for matches

    Args:
        demand_id: Demand ID
        params: Matching parameters:
            - age_min: Minimum age requirement
            - age_max: Maximum age requirement
            - japanese_level: Required Japanese level
            - english_level: Required English level
            - case_num: Maximum cases to generate
    """
    logger.info(f"Starting demand matching for demand_id={demand_id}, params={params}")

    try:
        async with async_session_context() as db:
            # Send analysis start notification
            send_demand_analysis_notification(demand_id, "match_start")

            # 1. Get demand AI data (or analyze if changed)
            ai_data = await get_demand_ai_data(demand_id, db)
            if not ai_data:
                logger.warning(f"No AI data for demand_id={demand_id}")
                send_demand_analysis_notification(demand_id, "match_error")
                return

            # 2. Delete old auto-matched cases
            await delete_old_matches(demand_id, db)

            # 3. Find matching supplies
            matches = await find_matching_supplies(
                demand_id=demand_id,
                ai_data=ai_data,
                params=params,
                db=db,
            )

            # 4. Create case records
            case_count = await create_case_records(
                demand_id=demand_id,
                ai_data=ai_data,
                matches=matches,
                db=db,
            )

            logger.info(
                f"Demand matching completed for demand_id={demand_id}, "
                f"created {case_count} cases"
            )

            # Send completion notification
            send_match_complete_notification(demand_id, case_count)

    except Exception as e:
        logger.error(f"Demand matching failed for demand_id={demand_id}: {e}")
        send_demand_analysis_notification(demand_id, "match_error")
        raise


async def get_demand_ai_data(
    demand_id: int,
    db: AsyncSession,
) -> dict[str, Any] | None:
    """
    Get or generate AI analysis data for a demand.

    If demand has changed (changeStatus=1), re-analyze using LLM.

    Returns:
        {
            "demand_txt": str,
            "xRaw": {...},
            "yRaw": {...},
            "zRaw": {...},
            "xyRaw": {...},
            "japaneseLevel": str,
            "englishLevel": str,
            "role": str,
            "fatherSkill": str,
        }
    """
    # TODO: Implement full logic from case_compare.get_demand_ai_data
    # 1. Check if demand has changeStatus=1
    # 2. If changed, call LLM to analyze X/Y/Z skills
    # 3. Update demand record with analysis results
    # 4. Return analysis data

    from app.services.rk.demand import demand_service

    demand = await demand_service.get_by_id(db, demand_id)
    if not demand:
        return None

    # Placeholder: Return basic data
    return {
        "demand_txt": demand.remark or "",
        "xRaw": {},
        "yRaw": {},
        "zRaw": {},
        "xyRaw": {},
        "japaneseLevel": demand.japaneseLevel or "",
        "englishLevel": demand.englishLevel or "",
        "role": demand.role or "",
        "fatherSkill": demand.fatherSkill or "",
    }


async def delete_old_matches(
    demand_id: int,
    db: AsyncSession,
) -> int:
    """
    Delete old auto-matched cases that are not yet in progress.

    Returns:
        Number of deleted cases
    """
    from app.services.rk.case import case_service

    return await case_service.delete_auto_matches(db, demand_id)


async def find_matching_supplies(
    demand_id: int,
    ai_data: dict[str, Any],
    params: dict[str, Any],
    db: AsyncSession,
) -> list[dict[str, Any]]:
    """
    Find supplies matching demand requirements.

    Matching algorithm:
    1. Search supplies with matching X/Z skills
    2. Calculate scores based on:
       - X skill match with Y level requirements
       - Z skill match
       - Language level requirements
       - Age requirements
    3. Filter and rank by score

    Returns:
        List of matches: [{"supply_id": int, "score": float, ...}]
    """
    # TODO: Implement full matching algorithm from case_compare.case_compare_service
    # This is complex logic involving:
    # - Extracting skill requirements from ai_data
    # - Searching supplies by skills
    # - Calculating match scores
    # - Filtering by language and age requirements

    return []


async def create_case_records(
    demand_id: int,
    ai_data: dict[str, Any],
    matches: list[dict[str, Any]],
    db: AsyncSession,
) -> int:
    """
    Create case records for matches.

    Args:
        demand_id: Demand ID
        ai_data: Demand AI analysis data
        matches: List of matches

    Returns:
        Number of cases created
    """
    from app.services.rk.case import case_service

    count = 0
    for match in matches:
        case_data = {
            "demandText": ai_data.get("demand_txt", ""),
            "demandId": demand_id,
            "supplyId": match["supply_id"],
            "score": match.get("score", 0),
            "result": match.get("result", ""),
            "years": match.get("match_years", 0),
            "supplyDemandStatus3": "待确认",
            "supplyDemandStatus4": match.get("status4", ""),
            "supplyDemandStatus5": "自动匹配",
            "fatherSkill": ai_data.get("fatherSkill", ""),
        }
        await case_service.create_if_not_exists(db, case_data)
        count += 1

    return count


__all__ = [
    "case_compare_service",
    "get_demand_ai_data",
    "delete_old_matches",
    "find_matching_supplies",
    "create_case_records",
]

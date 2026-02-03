"""
AI callback processor.

Processes callbacks from third-party AI analysis service.

Reference:
- assistant_py/app/v1/service/resume_updater.py
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rk import AnalysisStatus
from app.services.rk.demand import demand_service
from app.services.rk.supply import supply_service

logger = logging.getLogger("work_assistant.ai.callback")


async def process_callback_payload(
    payload: dict[str, Any],
    db: AsyncSession,
) -> None:
    """
    Process callback payload from third-party AI service.

    Args:
        payload: Callback payload containing analysis results
        db: Database session
    """
    event_type = payload.get("event_type", "")
    ext_unique_id = payload.get("ext_unique_id")
    extra_data = payload.get("extra_data", {})
    result = payload.get("result", {})
    error = payload.get("error")

    logger.info(f"Processing callback: event_type={event_type}, id={ext_unique_id}")

    try:
        if event_type == "resume_analyze":
            await _process_resume_analysis(db, ext_unique_id, extra_data, result, error)
        elif event_type == "resume_proposal_analyze":
            await _process_proposal_analysis(db, ext_unique_id, result, error)
        elif event_type == "demand_analyze":
            await _process_demand_analysis(db, ext_unique_id, extra_data, result, error)
        elif event_type == "match_analyze":
            await _process_match_analysis(db, ext_unique_id, extra_data, result, error)
        else:
            logger.warning(f"Unknown event type: {event_type}")

    except Exception as e:
        logger.error(f"Failed to process callback for {event_type}: {e}")
        raise


async def _process_resume_analysis(
    db: AsyncSession,
    supply_id: int,
    extra_data: dict,
    result: dict,
    error: str | None,
) -> None:
    """Process resume analysis callback."""
    if error:
        logger.error(f"Resume analysis error for supply {supply_id}: {error}")
        await supply_service.update_analysis_status(
            db, supply_id, AnalysisStatus.ANALYSIS_ERROR.value
        )
        return

    version = extra_data.get("version", 1)

    # Extract and save analysis results
    # Result structure depends on the third-party service
    basic_info = result.get("basic_info", {})
    work_experience = result.get("work_experience", [])
    skills = result.get("skills", {})

    # Update supply with extracted info
    update_data = {}

    if basic_info:
        if basic_info.get("name"):
            update_data["supplyUserName"] = basic_info["name"]
        if basic_info.get("age"):
            update_data["supplyUserAge"] = str(basic_info["age"])
        if basic_info.get("gender"):
            update_data["supplyUserGender"] = basic_info["gender"]
        if basic_info.get("nationality"):
            update_data["supplyUserCitizenship"] = basic_info["nationality"]
        if basic_info.get("japanese_level"):
            update_data["japaneseLevel"] = basic_info["japanese_level"]
        if basic_info.get("english_level"):
            update_data["englishLevel"] = basic_info["english_level"]

    if skills:
        if skills.get("x"):
            update_data["skillx"] = skills["x"]
        if skills.get("y"):
            update_data["skilly"] = skills["y"]
        if skills.get("z"):
            update_data["skillz"] = skills["z"]

    if update_data:
        await supply_service.update(db, supply_id, update_data)

    # Save AI data
    await supply_service.save_ai_data(
        db,
        supply_id,
        {
            "basic": basic_info,
            "workExperience": work_experience,
            "xData": skills.get("x_data"),
            "yData": skills.get("y_data"),
            "zData": skills.get("z_data"),
            "xRaw": skills.get("x_raw"),
            "yRaw": skills.get("y_raw"),
            "zRaw": skills.get("z_raw"),
        },
    )

    # Update analysis status
    await supply_service.update_analysis_status(
        db, supply_id, AnalysisStatus.ANALYSIS_DONE.value
    )

    logger.info(f"Resume analysis completed for supply {supply_id}")

    # TODO: Send MQTT notification


async def _process_proposal_analysis(
    db: AsyncSession,
    supply_id: int,
    result: dict,
    error: str | None,
) -> None:
    """Process proposal document analysis callback."""
    if error:
        logger.error(f"Proposal analysis error for supply {supply_id}: {error}")
        await supply_service.update_analysis_status(
            db, supply_id, AnalysisStatus.CONTACT_ANALYSIS_ERROR.value
        )
        return

    # Process proposal analysis result
    # The result structure depends on the third-party service

    await supply_service.update_analysis_status(
        db, supply_id, AnalysisStatus.CONTACT_ANALYSIS_DONE.value
    )

    logger.info(f"Proposal analysis completed for supply {supply_id}")


async def _process_demand_analysis(
    db: AsyncSession,
    demand_id: int,
    extra_data: dict,
    result: dict,
    error: str | None,
) -> None:
    """Process demand analysis callback."""
    if error:
        logger.error(f"Demand analysis error for demand {demand_id}: {error}")
        await demand_service.update_analysis_status(
            db, demand_id, AnalysisStatus.ANALYSIS_ERROR.value
        )
        return

    version = extra_data.get("version", 1)

    # Save AI data
    await demand_service.save_ai_data(db, demand_id, result)

    # Update analysis status
    await demand_service.update_analysis_status(
        db, demand_id, AnalysisStatus.ANALYSIS_DONE.value
    )

    logger.info(f"Demand analysis completed for demand {demand_id}")


async def _process_match_analysis(
    db: AsyncSession,
    demand_id: int,
    extra_data: dict,
    result: dict,
    error: str | None,
) -> None:
    """Process match analysis callback."""
    from app.services.rk.case import case_service

    if error:
        logger.error(f"Match analysis error for demand {demand_id}: {error}")
        await demand_service.update_analysis_status(
            db, demand_id, AnalysisStatus.MATCH_ERROR.value
        )
        return

    demand_version = extra_data.get("demand_version", 1)
    match_results = result.get("match_results", [])

    # Save match results
    for match in match_results:
        supply_id = match.get("supply_id")
        if not supply_id:
            continue

        await case_service.save_match_result(
            db,
            {
                "demand_id": demand_id,
                "supply_id": supply_id,
                "score": match.get("score", 0),
                "warning_msg": match.get("warning_msg"),
                "demand_role": match.get("demand_role"),
                "years_data": match.get("years_data"),
                "demand_version": demand_version,
                "supply_version": match.get("supply_version", 1),
                "msg": match.get("msg"),
            },
        )

    # Update analysis status
    await demand_service.update_analysis_status(
        db, demand_id, AnalysisStatus.MATCH_DONE.value
    )

    logger.info(
        f"Match analysis completed for demand {demand_id}, {len(match_results)} results"
    )

    # TODO: Send MQTT notification

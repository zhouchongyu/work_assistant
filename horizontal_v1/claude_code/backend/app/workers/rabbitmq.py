"""
RabbitMQ consumers for background processing.

Implements message-driven workers for:
- Resume extraction (consumer_extract_in)
- Demand matching (consumer_compare_in)

Reference:
- assistant_py/main.py
- Wiki: 系统架构/消息队列系统.md
"""

import logging
import traceback

from faststream.rabbit import RabbitQueue, RabbitRouter

from app.core.config import settings
from app.core.redis import DistributedLock

logger = logging.getLogger("work_assistant.workers.rabbitmq")

# Create RabbitMQ router with heartbeat
RABBIT_URL = settings.rabbitmq.full_url
router = RabbitRouter(RABBIT_URL, max_consumers=settings.rabbitmq.max_consumers)

# Queue definitions
consumer_extract_in_queue = RabbitQueue("consumer_extract_in", durable=True)
consumer_extract_out_queue = RabbitQueue("consumer_extract_out", durable=True)
consumer_compare_in_queue = RabbitQueue("consumer_compare_in", durable=True)
consumer_compare_out_queue = RabbitQueue("consumer_compare_out", durable=True)


@router.subscriber(consumer_extract_in_queue)
async def consumer_extract(message: dict) -> None:
    """
    Process resume extraction messages.

    Message format:
    {
        "supply_id": int,
        "consumer": str,  # SharePoint URL
        "last_file_update": str | None
    }

    This consumer:
    1. Acquires distributed lock to prevent duplicate processing
    2. Fetches resume from SharePoint
    3. Extracts text and calls LLM for analysis
    4. Updates supply record with extracted data
    """
    try:
        logger.info(f"Processing consumer_extract: {message}")

        supply_id = message.get("supply_id")
        if not supply_id:
            logger.error("consumer_extract: supply_id missing, skipping message")
            return

        # Use distributed lock to prevent duplicate processing
        async with DistributedLock(f"consumer_extract:{supply_id}", expire=60) as acquired:
            if acquired:
                # Import here to avoid circular imports
                from app.services.rk.resume_processor import process_resume_extraction

                await process_resume_extraction(
                    supply_id=supply_id,
                    sharepoint_url=message.get("consumer", ""),
                    last_file_update=message.get("last_file_update"),
                )

                # Force garbage collection after processing
                import gc

                gc.collect()
            else:
                logger.warning(
                    f"consumer_extract:{supply_id} failed to acquire lock, skipping"
                )

    except Exception as e:
        logger.error(f"Error in consumer_extract: {e}\n{traceback.format_exc()}")


@router.subscriber(consumer_compare_in_queue)
@router.publisher(consumer_compare_out_queue)
async def consumer_compare(message: dict) -> dict | None:
    """
    Process demand matching messages.

    Message format:
    {
        "demand_id": int,
        "analysisYearsMinimum": int,  # Min work years
        "analysisYearsMaximum": int,  # Max work years
        "analysisSelectJapaneseLevel": str,  # Required Japanese level
        "analysisSelectEnglishLevel": str,  # Required English level
        "analysisCASECount": int  # Max cases to generate
    }

    This consumer:
    1. Analyzes demand requirements
    2. Searches for matching supplies
    3. Creates case records for matches
    """
    try:
        logger.info(f"Processing consumer_compare: {message}")

        demand_id = message.get("demand_id")
        if not demand_id:
            logger.error("consumer_compare: demand_id missing, skipping message")
            return None

        # Extract parameters
        params = {
            "age_min": message.get("analysisYearsMinimum", 0),
            "age_max": message.get("analysisYearsMaximum", 0),
            "japanese_level": message.get("analysisSelectJapaneseLevel", ""),
            "english_level": message.get("analysisSelectEnglishLevel", ""),
            "case_num": message.get("analysisCASECount", 0),
        }

        # Import here to avoid circular imports
        from app.services.rk.demand_matcher import case_compare_service

        await case_compare_service(demand_id, params)

        return {"demand_id": demand_id, "status": "completed"}

    except Exception as e:
        logger.error(f"Error in consumer_compare: {e}\n{traceback.format_exc()}")
        return {"demand_id": message.get("demand_id"), "status": "error", "error": str(e)}


async def publish_extract_message(supply_id: int, sharepoint_url: str, last_file_update: str | None = None) -> None:
    """
    Publish message to resume extraction queue.

    Args:
        supply_id: Supply ID
        sharepoint_url: SharePoint file URL
        last_file_update: Last known file update time
    """
    message = {
        "supply_id": supply_id,
        "consumer": sharepoint_url,
        "last_file_update": last_file_update,
    }
    await router.broker.publish(message, queue=consumer_extract_in_queue)
    logger.info(f"Published extract message for supply_id={supply_id}")


async def publish_compare_message(
    demand_id: int,
    age_min: int = 0,
    age_max: int = 0,
    japanese_level: str = "",
    english_level: str = "",
    case_num: int = 0,
) -> None:
    """
    Publish message to demand matching queue.

    Args:
        demand_id: Demand ID
        age_min: Minimum age requirement
        age_max: Maximum age requirement
        japanese_level: Required Japanese level
        english_level: Required English level
        case_num: Maximum number of cases to generate
    """
    message = {
        "demand_id": demand_id,
        "analysisYearsMinimum": age_min,
        "analysisYearsMaximum": age_max,
        "analysisSelectJapaneseLevel": japanese_level,
        "analysisSelectEnglishLevel": english_level,
        "analysisCASECount": case_num,
    }
    await router.broker.publish(message, queue=consumer_compare_in_queue)
    logger.info(f"Published compare message for demand_id={demand_id}")


__all__ = [
    "router",
    "publish_extract_message",
    "publish_compare_message",
]

"""
Background workers and RabbitMQ consumers module.

Provides:
- RabbitMQ consumers for resume extraction and demand matching
- Message publishing utilities

Reference:
- assistant_py/main.py
"""

from app.workers.rabbitmq import (
    router,
    publish_extract_message,
    publish_compare_message,
)

__all__ = [
    "router",
    "publish_extract_message",
    "publish_compare_message",
]

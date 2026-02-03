"""
Logging configuration for the application.

Uses structured JSON logging for better observability.

Reference:
- assistant_py/common/log.py: Original logging setup
- Wiki: 后端服务/Python后端服务/Python后端服务.md
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["timestamp"] = self.formatTime(record)

        # Add application context
        log_record["app"] = settings.app_name
        log_record["env"] = settings.environment


def setup_logging() -> None:
    """Configure application logging."""
    # Create JSON formatter
    formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    loggers_config = {
        "work_assistant": logging.DEBUG if settings.debug else logging.INFO,
        "work_assistant.http": logging.INFO,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "aio_pika": logging.WARNING,
        "aiomqtt": logging.WARNING,
    }

    for logger_name, level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(f"work_assistant.{name}")

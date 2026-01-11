"""Logging configuration for the Raton bot."""

from __future__ import annotations

import logging.config
from typing import Any


def get_logging_config(level: str = "INFO") -> dict[str, Any]:
    """Get logging configuration dictionary.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Logging configuration dictionary for use with logging.config.dictConfig.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "{asctime} | {levelname:<8} | {name}:{funcName}:{lineno} | {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "raton.logging_config.JsonFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level.upper(),
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": level.upper(),
            "handlers": ["console"],
        },
        "loggers": {
            "raton": {
                "level": level.upper(),
                "handlers": ["console"],
                "propagate": False,
            },
            "httpx": {
                "level": "WARNING",
            },
            "httpcore": {
                "level": "WARNING",
            },
        },
    }


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON-formatted log string.
        """
        import json
        from datetime import UTC, datetime

        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
    """
    config = get_logging_config(level)
    logging.config.dictConfig(config)

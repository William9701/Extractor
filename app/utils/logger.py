"""
Structured logging configuration
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup structured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    return logger


def sanitize_pii(data: Any) -> Any:
    """
    Sanitize PII from data before logging
    Replace sensitive field values with [REDACTED]
    """
    if isinstance(data, dict):
        sanitized = {}
        pii_fields = {
            "full_name",
            "name",
            "address",
            "date_of_birth",
            "dob",
            "id_number",
            "ssn",
            "phone",
            "email",
        }
        for key, value in data.items():
            if key.lower() in pii_fields:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_pii(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_pii(item) for item in data]
    else:
        return data


# Create default logger
logger = setup_logger("pii_service")

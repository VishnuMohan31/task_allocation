import json
import logging
from datetime import datetime, timezone

from core.config import settings


class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON with timestamp and log_level fields."""

    # Fields that are standard LogRecord attributes — not "extra" data.
    _STANDARD_ATTRS: frozenset[str] = frozenset(
        logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
        | {"message", "asctime"}
    )

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include any extra fields injected via logger.info(..., extra={...})
        for key, value in record.__dict__.items():
            if key not in self._STANDARD_ATTRS:
                log_entry[key] = value
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """Return a structured JSON logger for the given name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    return logger

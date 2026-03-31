import json
import logging
import logging.handlers
from datetime import datetime, timezone

from core.config import settings


class StructuredFormatter(logging.Formatter):
    """Formats log records as single-line JSON."""

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
        for key, value in record.__dict__.items():
            if key not in self._STANDARD_ATTRS:
                log_entry[key] = value
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def _build_handlers() -> list[logging.Handler]:
    formatter = StructuredFormatter()

    # Console handler — always on
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    handlers: list[logging.Handler] = [console]

    # File handler — rotating, written to log_dir/log_file_name
    try:
        log_path = settings.log_dir / settings.log_file_name
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except Exception as exc:  # noqa: BLE001
        # Never crash the app because logging failed — just warn on console
        console.emit(
            logging.LogRecord(
                "core.logging", logging.WARNING, "", 0,
                f"Could not set up file logging: {exc}", (), None,
            )
        )

    return handlers


_handlers = _build_handlers()


def get_logger(name: str) -> logging.Logger:
    """Return a structured JSON logger that writes to console + rotating file."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        for h in _handlers:
            logger.addHandler(h)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    return logger

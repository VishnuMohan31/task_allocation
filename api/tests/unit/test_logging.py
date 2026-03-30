import json
import logging

import pytest

from core.logging import get_logger


def test_get_logger_returns_logger():
    logger = get_logger("test.basic")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.basic"


def test_logger_emits_structured_record_with_required_fields(capsys):
    logger = get_logger("test.structured")
    logger.info("hello structured logging")

    captured = capsys.readouterr()
    record = json.loads(captured.err)

    assert "timestamp" in record
    assert "log_level" in record


def test_logger_log_level_matches_message_level(capsys):
    logger = get_logger("test.level")
    logger.warning("a warning message")

    captured = capsys.readouterr()
    record = json.loads(captured.err)

    assert record["log_level"] == "WARNING"


def test_logger_message_is_present(capsys):
    logger = get_logger("test.message")
    logger.info("check message field")

    captured = capsys.readouterr()
    record = json.loads(captured.err)

    assert record["message"] == "check message field"


def test_logger_timestamp_is_iso_format(capsys):
    from datetime import datetime

    logger = get_logger("test.timestamp")
    logger.info("timestamp check")

    captured = capsys.readouterr()
    record = json.loads(captured.err)

    # Should parse without error
    datetime.fromisoformat(record["timestamp"])

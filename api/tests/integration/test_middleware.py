"""Tests for LoggingMiddleware (app/middleware.py).

Verifies that every request produces exactly two structured log entries
(one for the incoming request, one for the outgoing response) and that
both entries share the same ``request_id``.
"""

import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware import LoggingMiddleware
from core.logging import StructuredFormatter


def _make_app() -> FastAPI:
    """Return a minimal FastAPI app with LoggingMiddleware attached."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"pong": True}

    return app


@pytest.fixture()
def client():
    return TestClient(_make_app())


# ---------------------------------------------------------------------------
# Helper: collect structured log records emitted by the middleware logger
# ---------------------------------------------------------------------------

class _JsonCollector(logging.Handler):
    """Captures log records and formats them as parsed JSON dicts."""

    def __init__(self):
        super().__init__()
        self.setFormatter(StructuredFormatter())
        self.entries: list[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.entries.append(json.loads(self.format(record)))


@pytest.fixture()
def log_collector():
    """Attach a JSON-collecting handler to the middleware logger."""
    collector = _JsonCollector()
    mw_logger = logging.getLogger("app.middleware")
    mw_logger.addHandler(collector)
    yield collector
    mw_logger.removeHandler(collector)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_middleware_emits_two_log_entries(client, log_collector):
    """A single request must produce exactly two log entries."""
    client.get("/ping")
    assert len(log_collector.entries) == 2, (
        f"Expected 2 log entries, got {len(log_collector.entries)}: {log_collector.entries}"
    )


def test_middleware_log_entries_share_request_id(client, log_collector):
    """Both log entries for a request must carry the same request_id."""
    client.get("/ping")

    entries = log_collector.entries
    assert len(entries) == 2

    assert "request_id" in entries[0], "request log entry missing request_id"
    assert "request_id" in entries[1], "response log entry missing request_id"
    assert entries[0]["request_id"] == entries[1]["request_id"], (
        "request_id must be identical across both log entries"
    )


def test_middleware_request_entry_contains_method_and_path(client, log_collector):
    """The first log entry must include HTTP method and path."""
    client.get("/ping")

    request_entry = log_collector.entries[0]
    assert request_entry.get("method") == "GET"
    assert request_entry.get("path") == "/ping"


def test_middleware_response_entry_contains_status_code(client, log_collector):
    """The second log entry must include the HTTP status code."""
    client.get("/ping")

    response_entry = log_collector.entries[1]
    assert response_entry.get("status_code") == 200


def test_middleware_response_entry_contains_duration(client, log_collector):
    """The response log entry must include a numeric duration_ms field."""
    client.get("/ping")

    response_entry = log_collector.entries[1]
    assert "duration_ms" in response_entry
    assert isinstance(response_entry["duration_ms"], (int, float))
    assert response_entry["duration_ms"] >= 0


def test_middleware_request_ids_are_unique_across_requests(client, log_collector):
    """Each request must receive a distinct request_id."""
    client.get("/ping")
    client.get("/ping")

    entries = log_collector.entries
    assert len(entries) == 4  # 2 entries × 2 requests

    ids = {e["request_id"] for e in entries}
    assert len(ids) == 2, "Each request must have a unique request_id"

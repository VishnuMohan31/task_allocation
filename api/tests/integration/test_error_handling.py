"""Tests for global exception handler behavior (task 3.2 — TDD).

These tests use a minimal FastAPI test app that deliberately raises each
exception type so we can verify the HTTP response shape once the handlers
are registered in task 3.3 (utils/error_handlers.py).

All tests are expected to FAIL until task 3.3 is implemented.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from utils.error_handlers import register_exception_handlers
from utils.exceptions import StoreCorruptedError, TaskNotFoundError

# ---------------------------------------------------------------------------
# Minimal test application
# ---------------------------------------------------------------------------

test_app = FastAPI()
register_exception_handlers(test_app)


@test_app.get("/raise/task-not-found")
def raise_task_not_found():
    raise TaskNotFoundError("test-id-123")


@test_app.get("/raise/store-corrupted")
def raise_store_corrupted():
    raise StoreCorruptedError("bad json at line 1")


@test_app.get("/raise/unhandled")
def raise_unhandled():
    raise RuntimeError("something went very wrong internally")


class _SampleBody(BaseModel):
    priority: int

    @field_validator("priority")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("priority must be >= 1")
        return v


@test_app.post("/raise/validation")
def raise_validation(body: _SampleBody):
    return {"priority": body.priority}


client = TestClient(test_app, raise_server_exceptions=False)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

ERROR_KEYS = {"error_code", "message", "details"}


def assert_error_shape(data: dict) -> None:
    """Assert the response body matches the ErrorResponse schema."""
    assert ERROR_KEYS == set(data.keys()), (
        f"Expected keys {ERROR_KEYS}, got {set(data.keys())}"
    )
    assert isinstance(data["error_code"], str) and data["error_code"]
    assert isinstance(data["message"], str) and data["message"]
    assert isinstance(data["details"], dict)


# ---------------------------------------------------------------------------
# Requirement 6.2 — TaskNotFoundError → 404 TASK_NOT_FOUND
# ---------------------------------------------------------------------------


def test_task_not_found_returns_404():
    """TaskNotFoundError must produce HTTP 404. (Req 6.2)"""
    response = client.get("/raise/task-not-found")
    assert response.status_code == 404


def test_task_not_found_error_code():
    """TaskNotFoundError response must carry error_code TASK_NOT_FOUND. (Req 6.2)"""
    response = client.get("/raise/task-not-found")
    data = response.json()
    assert data["error_code"] == "TASK_NOT_FOUND"


def test_task_not_found_response_shape():
    """TaskNotFoundError response must follow ErrorResponse schema. (Req 6.1)"""
    response = client.get("/raise/task-not-found")
    assert_error_shape(response.json())


def test_task_not_found_message_contains_task_id():
    """TaskNotFoundError message should reference the missing task id. (Req 6.2)"""
    response = client.get("/raise/task-not-found")
    assert "test-id-123" in response.json()["message"]


# ---------------------------------------------------------------------------
# Requirement 6.3 — StoreCorruptedError → 500 STORE_CORRUPTED
# ---------------------------------------------------------------------------


def test_store_corrupted_returns_500():
    """StoreCorruptedError must produce HTTP 500. (Req 6.3)"""
    response = client.get("/raise/store-corrupted")
    assert response.status_code == 500


def test_store_corrupted_error_code():
    """StoreCorruptedError response must carry error_code STORE_CORRUPTED. (Req 6.3)"""
    response = client.get("/raise/store-corrupted")
    data = response.json()
    assert data["error_code"] == "STORE_CORRUPTED"


def test_store_corrupted_response_shape():
    """StoreCorruptedError response must follow ErrorResponse schema. (Req 6.1)"""
    response = client.get("/raise/store-corrupted")
    assert_error_shape(response.json())


# ---------------------------------------------------------------------------
# Requirement 6.4 — Unhandled exceptions → 500 INTERNAL_ERROR (no stack trace)
# ---------------------------------------------------------------------------


def test_unhandled_exception_returns_500():
    """Unhandled exceptions must produce HTTP 500. (Req 6.4)"""
    response = client.get("/raise/unhandled")
    assert response.status_code == 500


def test_unhandled_exception_error_code():
    """Unhandled exception response must carry error_code INTERNAL_ERROR. (Req 6.4)"""
    response = client.get("/raise/unhandled")
    data = response.json()
    assert data["error_code"] == "INTERNAL_ERROR"


def test_unhandled_exception_response_shape():
    """Unhandled exception response must follow ErrorResponse schema. (Req 6.1)"""
    response = client.get("/raise/unhandled")
    assert_error_shape(response.json())


def test_unhandled_exception_no_stack_trace():
    """Unhandled exception response MUST NOT expose internal stack traces. (Req 6.4)"""
    response = client.get("/raise/unhandled")
    body = response.text
    # Stack trace indicators that must not appear in the response body
    assert "Traceback" not in body
    assert "RuntimeError" not in body
    assert "something went very wrong internally" not in body


# ---------------------------------------------------------------------------
# Requirement 6.5 — Pydantic ValidationError → 422 VALIDATION_ERROR
# ---------------------------------------------------------------------------


def test_validation_error_returns_422():
    """Pydantic ValidationError must produce HTTP 422. (Req 6.5)"""
    response = client.post("/raise/validation", json={"priority": 0})
    assert response.status_code == 422


def test_validation_error_error_code():
    """Pydantic ValidationError response must carry error_code VALIDATION_ERROR. (Req 6.5)"""
    response = client.post("/raise/validation", json={"priority": 0})
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


def test_validation_error_response_shape():
    """Pydantic ValidationError response must follow ErrorResponse schema. (Req 6.1)"""
    response = client.post("/raise/validation", json={"priority": 0})
    assert_error_shape(response.json())


def test_validation_error_missing_field_returns_422():
    """Missing required field must also produce HTTP 422. (Req 6.5)"""
    response = client.post("/raise/validation", json={})
    assert response.status_code == 422


def test_validation_error_missing_field_error_code():
    """Missing required field response must carry error_code VALIDATION_ERROR. (Req 6.5)"""
    response = client.post("/raise/validation", json={})
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"

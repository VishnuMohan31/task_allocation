"""Tests for custom exception classes in utils/exceptions.py."""

import pytest

from utils.exceptions import StoreCorruptedError, TaskNotFoundError


def test_task_not_found_error_code():
    """TaskNotFoundError carries error_code TASK_NOT_FOUND."""
    exc = TaskNotFoundError("abc-123")
    assert exc.error_code == "TASK_NOT_FOUND"


def test_task_not_found_http_status():
    assert TaskNotFoundError("x").http_status == 404


def test_task_not_found_message():
    exc = TaskNotFoundError("abc-123")
    assert "abc-123" in str(exc)


def test_task_not_found_is_exception():
    with pytest.raises(TaskNotFoundError):
        raise TaskNotFoundError("some-id")


def test_store_corrupted_error_code():
    """StoreCorruptedError carries error_code STORE_CORRUPTED."""
    exc = StoreCorruptedError()
    assert exc.error_code == "STORE_CORRUPTED"


def test_store_corrupted_http_status():
    assert StoreCorruptedError().http_status == 500


def test_store_corrupted_default_message():
    exc = StoreCorruptedError()
    assert "corrupted" in str(exc).lower()


def test_store_corrupted_custom_message():
    exc = StoreCorruptedError("bad json at line 3")
    assert "bad json" in str(exc)


def test_store_corrupted_is_exception():
    with pytest.raises(StoreCorruptedError):
        raise StoreCorruptedError()

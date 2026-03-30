"""Tests for TaskService — written TDD-style before implementation (task 7.1).

Covers (Requirement 8.3):
  - Successful task creation
  - Successful task completion
  - Completion of a non-existent task (TaskNotFoundError)
"""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, call
from uuid import uuid4

import pytest

from models.task import Task, TaskCreate
from utils.exceptions import TaskNotFoundError

# TaskService does not exist yet — import will fail until task 7.2 is done.
from services.task_service import TaskService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=str(uuid4()),
        title="Sample task",
        description="",
        priority=3,
        tags=[],
        completed=False,
        created_at=datetime.utcnow(),
        completed_at=None,
    )
    defaults.update(kwargs)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------

class TestCreateTask:
    """Tests for TaskService.create_task."""

    def test_create_task_returns_task_with_uuid(self):
        """Returned task must have a non-empty UUID id."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t  # echo back the task

        service = TaskService(repo=repo)
        task_in = TaskCreate(title="Buy milk", priority=2)

        result = service.create_task(task_in)

        assert result.id, "id must be a non-empty string"
        # Should look like a UUID4
        import uuid
        uuid.UUID(result.id, version=4)  # raises ValueError if not valid UUID4

    def test_create_task_sets_completed_false(self):
        """Newly created task must have completed=False."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        task_in = TaskCreate(title="Write tests", priority=5)

        result = service.create_task(task_in)

        assert result.completed is False

    def test_create_task_sets_created_at(self):
        """Newly created task must have created_at set to a recent UTC datetime."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        before = datetime.utcnow()
        task_in = TaskCreate(title="Deploy app", priority=4)

        result = service.create_task(task_in)

        after = datetime.utcnow()
        assert before <= result.created_at <= after, (
            "created_at must be set to current UTC time"
        )

    def test_create_task_persists_via_repository(self):
        """create_task must call repo.save_task exactly once with the new task."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        task_in = TaskCreate(title="Refactor code", priority=3)

        result = service.create_task(task_in)

        repo.save_task.assert_called_once()
        saved_task = repo.save_task.call_args[0][0]
        assert saved_task.id == result.id

    def test_create_task_copies_title_and_fields(self):
        """Task fields must match the TaskCreate input."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        task_in = TaskCreate(
            title="Read a book",
            description="Fiction",
            priority=1,
            tags=["leisure"],
        )

        result = service.create_task(task_in)

        assert result.title == "Read a book"
        assert result.description == "Fiction"
        assert result.priority == 1
        assert result.tags == ["leisure"]

    def test_create_task_completed_at_is_none(self):
        """completed_at must be None for a newly created task."""
        repo = MagicMock()
        repo.save_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        task_in = TaskCreate(title="Plan sprint", priority=3)

        result = service.create_task(task_in)

        assert result.completed_at is None


# ---------------------------------------------------------------------------
# complete_task
# ---------------------------------------------------------------------------

class TestCompleteTask:
    """Tests for TaskService.complete_task."""

    def test_complete_task_returns_task_with_completed_true(self):
        """Completing a task must set completed=True on the returned task."""
        existing = _make_task(completed=False)
        repo = MagicMock()
        repo.get_task.return_value = existing
        repo.update_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        result = service.complete_task(existing.id)

        assert result.completed is True

    def test_complete_task_sets_completed_at(self):
        """completed_at must be set to a recent UTC datetime after completion."""
        existing = _make_task(completed=False)
        repo = MagicMock()
        repo.get_task.return_value = existing
        repo.update_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        before = datetime.utcnow()
        result = service.complete_task(existing.id)
        after = datetime.utcnow()

        assert result.completed_at is not None
        assert before <= result.completed_at <= after, (
            "completed_at must be set to current UTC time"
        )

    def test_complete_task_persists_via_repository(self):
        """complete_task must call repo.update_task exactly once with the updated task."""
        existing = _make_task(completed=False)
        repo = MagicMock()
        repo.get_task.return_value = existing
        repo.update_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        result = service.complete_task(existing.id)

        repo.update_task.assert_called_once()
        updated_task = repo.update_task.call_args[0][0]
        assert updated_task.id == existing.id
        assert updated_task.completed is True

    def test_complete_task_fetches_correct_task(self):
        """complete_task must call repo.get_task with the given task_id."""
        existing = _make_task(completed=False)
        repo = MagicMock()
        repo.get_task.return_value = existing
        repo.update_task.side_effect = lambda t: t

        service = TaskService(repo=repo)
        service.complete_task(existing.id)

        repo.get_task.assert_called_once_with(existing.id)

    def test_complete_task_raises_task_not_found_error(self):
        """complete_task must raise TaskNotFoundError when task_id does not exist."""
        repo = MagicMock()
        repo.get_task.side_effect = TaskNotFoundError("nonexistent-id")

        service = TaskService(repo=repo)

        with pytest.raises(TaskNotFoundError) as exc_info:
            service.complete_task("nonexistent-id")

        assert exc_info.value.task_id == "nonexistent-id"

    def test_complete_task_not_found_error_has_correct_error_code(self):
        """TaskNotFoundError raised by complete_task must carry the correct error_code."""
        repo = MagicMock()
        repo.get_task.side_effect = TaskNotFoundError("missing-id")

        service = TaskService(repo=repo)

        with pytest.raises(TaskNotFoundError) as exc_info:
            service.complete_task("missing-id")

        assert exc_info.value.error_code == "TASK_NOT_FOUND"

    def test_complete_task_does_not_call_update_when_not_found(self):
        """repo.update_task must NOT be called when the task does not exist."""
        repo = MagicMock()
        repo.get_task.side_effect = TaskNotFoundError("ghost-id")

        service = TaskService(repo=repo)

        with pytest.raises(TaskNotFoundError):
            service.complete_task("ghost-id")

        repo.update_task.assert_not_called()

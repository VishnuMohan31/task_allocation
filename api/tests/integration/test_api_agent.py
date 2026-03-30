"""Tests for the agent decision HTTP endpoint — written TDD-style before implementation (task 8.2).

Covers (Requirements 2.1–2.5, 8.5):
  - GET /agent/decision: returns 200 with correct shape
  - GET /agent/decision: next_task is highest-priority pending task
  - GET /agent/decision: next_task is null when all tasks completed
  - GET /agent/decision: next_task is null and score is 0.0 when no tasks exist
  - GET /agent/decision: productivity_score is always in [0.0, 1.0]
  - GET /agent/decision: suggestion is always a non-empty string

Uses FastAPI TestClient with the TaskRepository dependency overridden to use
a tmp_path-backed store (Requirement 8.5).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# These imports will fail until tasks 8.4 / 9.1 are implemented — that is expected.
from app.main import app
from repositories.task_repository import TaskRepository
from models.task import Task


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> TaskRepository:
    """Return a TaskRepository backed by a temporary directory."""
    return TaskRepository(store_path=tmp_path / "store.json")


@pytest.fixture()
def client(tmp_repo: TaskRepository) -> TestClient:
    """Return a TestClient with the TaskRepository dependency overridden."""
    from app.api.agent import get_repository  # dependency callable defined in router

    app.dependency_overrides[get_repository] = lambda: tmp_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(
    title: str = "Task",
    priority: int = 3,
    completed: bool = False,
    created_at: datetime | None = None,
) -> Task:
    return Task(
        title=title,
        description="",
        priority=priority,
        completed=completed,
        created_at=created_at or datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# GET /agent/decision — response shape
# ---------------------------------------------------------------------------


class TestAgentDecisionShape:
    """Tests for response structure (Requirement 2.1)."""

    def test_returns_200(self, client: TestClient, tmp_repo: TaskRepository) -> None:
        """GET /agent/decision must return HTTP 200."""
        response = client.get("/agent/decision")
        assert response.status_code == 200

    def test_response_has_next_task_field(self, client: TestClient) -> None:
        """Response must contain a next_task field."""
        response = client.get("/agent/decision")
        assert "next_task" in response.json()

    def test_response_has_productivity_score_field(self, client: TestClient) -> None:
        """Response must contain a productivity_score field."""
        response = client.get("/agent/decision")
        assert "productivity_score" in response.json()

    def test_response_has_suggestion_field(self, client: TestClient) -> None:
        """Response must contain a suggestion field."""
        response = client.get("/agent/decision")
        assert "suggestion" in response.json()

    def test_response_has_reasoning_field(self, client: TestClient) -> None:
        """Response must contain a reasoning field."""
        response = client.get("/agent/decision")
        assert "reasoning" in response.json()

    def test_reasoning_is_non_empty_string(self, client: TestClient) -> None:
        """reasoning must be a non-empty string."""
        response = client.get("/agent/decision")
        data = response.json()
        assert isinstance(data["reasoning"], str)
        assert data["reasoning"].strip() != ""

    def test_suggestion_is_non_empty_string(self, client: TestClient) -> None:
        """suggestion must be a non-empty string (Requirement 3.3)."""
        response = client.get("/agent/decision")
        data = response.json()
        assert isinstance(data["suggestion"], str)
        assert data["suggestion"].strip() != ""

    def test_productivity_score_is_float(self, client: TestClient) -> None:
        """productivity_score must be a numeric value."""
        response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert isinstance(score, (int, float))

    def test_productivity_score_in_unit_interval(self, client: TestClient) -> None:
        """productivity_score must be in [0.0, 1.0] (Requirement 2.5)."""
        response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# GET /agent/decision — empty store
# ---------------------------------------------------------------------------


class TestAgentDecisionEmptyStore:
    """Tests when no tasks exist (Requirement 2.4)."""

    def test_no_tasks_next_task_is_null(self, client: TestClient) -> None:
        """next_task must be null when no tasks exist (Requirement 2.4)."""
        response = client.get("/agent/decision")
        assert response.json()["next_task"] is None

    def test_no_tasks_score_is_zero(self, client: TestClient) -> None:
        """productivity_score must be 0.0 when no tasks exist (Requirement 2.4)."""
        response = client.get("/agent/decision")
        assert response.json()["productivity_score"] == 0.0

    def test_no_tasks_suggestion_is_non_empty(self, client: TestClient) -> None:
        """suggestion must still be non-empty when no tasks exist."""
        response = client.get("/agent/decision")
        assert response.json()["suggestion"].strip() != ""


# ---------------------------------------------------------------------------
# GET /agent/decision — task selection logic
# ---------------------------------------------------------------------------


class TestAgentDecisionTaskSelection:
    """Tests for next_task selection logic (Requirement 2.2, 2.3)."""

    def test_single_pending_task_is_returned(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """next_task must be the only pending task."""
        task = _make_task(title="Only task", priority=3)
        tmp_repo.save_task(task)

        response = client.get("/agent/decision")
        data = response.json()
        assert data["next_task"] is not None
        assert data["next_task"]["id"] == task.id

    def test_highest_priority_task_selected(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """next_task must be the pending task with the highest priority (Requirement 2.2)."""
        low = _make_task(title="Low priority", priority=1)
        high = _make_task(title="High priority", priority=5)
        mid = _make_task(title="Mid priority", priority=3)
        for t in [low, mid, high]:
            tmp_repo.save_task(t)

        response = client.get("/agent/decision")
        assert response.json()["next_task"]["id"] == high.id

    def test_tie_broken_by_created_at(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """When priorities are equal, the earliest created_at wins (Requirement 2.2)."""
        now = datetime.utcnow()
        earlier = _make_task(title="Earlier", priority=4, created_at=now - timedelta(hours=1))
        later = _make_task(title="Later", priority=4, created_at=now)
        tmp_repo.save_task(later)
        tmp_repo.save_task(earlier)

        response = client.get("/agent/decision")
        assert response.json()["next_task"]["id"] == earlier.id

    def test_completed_tasks_excluded_from_selection(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """Completed tasks must not be selected as next_task."""
        done = _make_task(title="Done", priority=5, completed=True)
        pending = _make_task(title="Pending", priority=1)
        tmp_repo.save_task(done)
        tmp_repo.save_task(pending)

        response = client.get("/agent/decision")
        assert response.json()["next_task"]["id"] == pending.id

    def test_all_tasks_completed_next_task_is_null(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """next_task must be null when all tasks are completed (Requirement 2.3)."""
        done1 = _make_task(title="Done 1", priority=3, completed=True)
        done2 = _make_task(title="Done 2", priority=5, completed=True)
        tmp_repo.save_task(done1)
        tmp_repo.save_task(done2)

        response = client.get("/agent/decision")
        assert response.json()["next_task"] is None

    def test_all_tasks_completed_suggestion_indicates_done(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """suggestion must indicate all tasks are done when all are completed (Requirement 2.3)."""
        done = _make_task(title="Done", priority=3, completed=True)
        tmp_repo.save_task(done)

        response = client.get("/agent/decision")
        suggestion = response.json()["suggestion"]
        assert "All tasks complete" in suggestion


# ---------------------------------------------------------------------------
# GET /agent/decision — productivity score
# ---------------------------------------------------------------------------


class TestAgentDecisionProductivityScore:
    """Tests for productivity_score calculation (Requirement 2.5)."""

    def test_score_zero_when_no_tasks_completed(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """productivity_score must be 0.0 when no tasks are completed."""
        tmp_repo.save_task(_make_task(priority=3))
        tmp_repo.save_task(_make_task(priority=5))

        response = client.get("/agent/decision")
        assert response.json()["productivity_score"] == 0.0

    def test_score_one_when_all_tasks_completed(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """productivity_score must be 1.0 when all tasks are completed."""
        tmp_repo.save_task(_make_task(priority=3, completed=True))
        tmp_repo.save_task(_make_task(priority=5, completed=True))

        response = client.get("/agent/decision")
        assert response.json()["productivity_score"] == 1.0

    def test_score_in_unit_interval_with_mixed_tasks(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """productivity_score must be in [0.0, 1.0] for any mix of tasks (Requirement 2.5)."""
        tmp_repo.save_task(_make_task(priority=4, completed=True))
        tmp_repo.save_task(_make_task(priority=1, completed=False))

        response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert 0.0 <= score <= 1.0

    def test_score_weighted_by_priority(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """productivity_score must be weighted by task priority."""
        # priority 4 done, priority 1 pending → 4 / (4+1) = 0.8
        tmp_repo.save_task(_make_task(priority=4, completed=True))
        tmp_repo.save_task(_make_task(priority=1, completed=False))

        response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert abs(score - 0.8) < 1e-9


# ---------------------------------------------------------------------------
# GET /agent/decision — next_task field shape
# ---------------------------------------------------------------------------


class TestAgentDecisionNextTaskShape:
    """Tests for the shape of the next_task object when present."""

    def test_next_task_has_id(self, client: TestClient, tmp_repo: TaskRepository) -> None:
        tmp_repo.save_task(_make_task(title="Task A", priority=2))
        data = client.get("/agent/decision").json()
        assert "id" in data["next_task"]

    def test_next_task_has_title(self, client: TestClient, tmp_repo: TaskRepository) -> None:
        tmp_repo.save_task(_make_task(title="Task A", priority=2))
        data = client.get("/agent/decision").json()
        assert data["next_task"]["title"] == "Task A"

    def test_next_task_has_priority(self, client: TestClient, tmp_repo: TaskRepository) -> None:
        tmp_repo.save_task(_make_task(title="Task A", priority=2))
        data = client.get("/agent/decision").json()
        assert data["next_task"]["priority"] == 2

    def test_next_task_completed_is_false(
        self, client: TestClient, tmp_repo: TaskRepository
    ) -> None:
        """next_task must be a pending (not completed) task."""
        tmp_repo.save_task(_make_task(title="Task A", priority=2))
        data = client.get("/agent/decision").json()
        assert data["next_task"]["completed"] is False

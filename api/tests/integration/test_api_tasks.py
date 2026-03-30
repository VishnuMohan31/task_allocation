"""Tests for task HTTP endpoints — written TDD-style before implementation (task 8.1).

Covers (Requirements 1.1, 1.2, 1.3, 1.4, 8.5):
  - POST /tasks: successful creation (201)
  - POST /tasks: invalid payload (422)
  - POST /tasks/{task_id}/complete: successful completion (200)
  - POST /tasks/{task_id}/complete: task not found (404)

Uses FastAPI TestClient with the TaskRepository dependency overridden to use
a tmp_path-backed in-memory store (Requirement 8.5).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# These imports will fail until task 8.3 / 9.1 are implemented — that is expected.
from app.main import app
from repositories.task_repository import TaskRepository


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
    from app.api.tasks import get_repository  # dependency callable defined in router

    app.dependency_overrides[get_repository] = lambda: tmp_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /tasks — create task
# ---------------------------------------------------------------------------


class TestCreateTask:
    """Tests for POST /tasks (Requirement 1.1, 1.4)."""

    def test_create_task_returns_201(self, client: TestClient) -> None:
        """Valid payload must return HTTP 201."""
        response = client.post("/tasks", json={"title": "Buy milk", "priority": 2})
        assert response.status_code == 201

    def test_create_task_response_has_uuid_id(self, client: TestClient) -> None:
        """Response must contain a valid UUID4 id."""
        import uuid

        response = client.post("/tasks", json={"title": "Buy milk", "priority": 2})
        data = response.json()
        assert "id" in data
        uuid.UUID(data["id"], version=4)  # raises ValueError if not valid UUID4

    def test_create_task_response_completed_false(self, client: TestClient) -> None:
        """Newly created task must have completed=false."""
        response = client.post("/tasks", json={"title": "Buy milk", "priority": 2})
        assert response.json()["completed"] is False

    def test_create_task_response_has_created_at(self, client: TestClient) -> None:
        """Response must contain a created_at timestamp."""
        response = client.post("/tasks", json={"title": "Buy milk", "priority": 2})
        data = response.json()
        assert "created_at" in data
        # Must be parseable as a datetime
        datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))

    def test_create_task_response_completed_at_is_null(self, client: TestClient) -> None:
        """completed_at must be null for a newly created task."""
        response = client.post("/tasks", json={"title": "Buy milk", "priority": 2})
        assert response.json()["completed_at"] is None

    def test_create_task_echoes_title_and_priority(self, client: TestClient) -> None:
        """Response must echo back the title and priority from the request."""
        response = client.post(
            "/tasks",
            json={"title": "Write tests", "priority": 5, "description": "TDD", "tags": ["dev"]},
        )
        data = response.json()
        assert data["title"] == "Write tests"
        assert data["priority"] == 5
        assert data["description"] == "TDD"
        assert data["tags"] == ["dev"]

    def test_create_task_missing_title_returns_422(self, client: TestClient) -> None:
        """Missing title must return HTTP 422 (Requirement 1.4)."""
        response = client.post("/tasks", json={"priority": 3})
        assert response.status_code == 422

    def test_create_task_empty_title_returns_422(self, client: TestClient) -> None:
        """Empty/whitespace title must return HTTP 422 (Requirement 1.4)."""
        response = client.post("/tasks", json={"title": "   ", "priority": 3})
        assert response.status_code == 422

    def test_create_task_priority_too_low_returns_422(self, client: TestClient) -> None:
        """Priority below 1 must return HTTP 422 (Requirement 1.4)."""
        response = client.post("/tasks", json={"title": "Task", "priority": 0})
        assert response.status_code == 422

    def test_create_task_priority_too_high_returns_422(self, client: TestClient) -> None:
        """Priority above 5 must return HTTP 422 (Requirement 1.4)."""
        response = client.post("/tasks", json={"title": "Task", "priority": 6})
        assert response.status_code == 422

    def test_create_task_missing_priority_returns_422(self, client: TestClient) -> None:
        """Missing priority must return HTTP 422 (Requirement 1.4)."""
        response = client.post("/tasks", json={"title": "Task"})
        assert response.status_code == 422

    def test_create_task_422_response_has_error_code(self, client: TestClient) -> None:
        """422 response must include error_code field (Requirement 6.1)."""
        response = client.post("/tasks", json={"priority": 3})
        data = response.json()
        assert data.get("error_code") == "VALIDATION_ERROR"

    def test_create_task_422_response_has_message(self, client: TestClient) -> None:
        """422 response must include a message field."""
        response = client.post("/tasks", json={"priority": 3})
        data = response.json()
        assert "message" in data
        assert data["message"]

    def test_create_task_422_response_has_details(self, client: TestClient) -> None:
        """422 response must include a details field."""
        response = client.post("/tasks", json={"priority": 3})
        data = response.json()
        assert "details" in data


# ---------------------------------------------------------------------------
# POST /tasks/{task_id}/complete — complete task
# ---------------------------------------------------------------------------


class TestCompleteTask:
    """Tests for POST /tasks/{task_id}/complete (Requirements 1.2, 1.3)."""

    def _create_task(self, client: TestClient, title: str = "Sample", priority: int = 3) -> dict:
        """Helper: create a task and return the response JSON."""
        response = client.post("/tasks", json={"title": title, "priority": priority})
        assert response.status_code == 201
        return response.json()

    def test_complete_task_returns_200(self, client: TestClient) -> None:
        """Completing an existing task must return HTTP 200 (Requirement 1.2)."""
        task = self._create_task(client)
        response = client.post(f"/tasks/{task['id']}/complete")
        assert response.status_code == 200

    def test_complete_task_sets_completed_true(self, client: TestClient) -> None:
        """Response must have completed=true after completion (Requirement 1.2)."""
        task = self._create_task(client)
        response = client.post(f"/tasks/{task['id']}/complete")
        assert response.json()["completed"] is True

    def test_complete_task_sets_completed_at(self, client: TestClient) -> None:
        """completed_at must be set to a non-null datetime after completion (Requirement 1.2)."""
        task = self._create_task(client)
        response = client.post(f"/tasks/{task['id']}/complete")
        data = response.json()
        assert data["completed_at"] is not None
        datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))

    def test_complete_task_preserves_task_fields(self, client: TestClient) -> None:
        """Completing a task must not alter its title, priority, or description."""
        task = self._create_task(client, title="Important task", priority=4)
        response = client.post(f"/tasks/{task['id']}/complete")
        data = response.json()
        assert data["id"] == task["id"]
        assert data["title"] == task["title"]
        assert data["priority"] == task["priority"]

    def test_complete_nonexistent_task_returns_404(self, client: TestClient) -> None:
        """Completing a non-existent task must return HTTP 404 (Requirement 1.3)."""
        fake_id = str(uuid4())
        response = client.post(f"/tasks/{fake_id}/complete")
        assert response.status_code == 404

    def test_complete_nonexistent_task_error_code(self, client: TestClient) -> None:
        """404 response must include error_code: TASK_NOT_FOUND (Requirement 1.3)."""
        fake_id = str(uuid4())
        response = client.post(f"/tasks/{fake_id}/complete")
        data = response.json()
        assert data.get("error_code") == "TASK_NOT_FOUND"

    def test_complete_nonexistent_task_has_message(self, client: TestClient) -> None:
        """404 response must include a non-empty message (Requirement 1.3)."""
        fake_id = str(uuid4())
        response = client.post(f"/tasks/{fake_id}/complete")
        data = response.json()
        assert "message" in data
        assert data["message"]

    def test_complete_nonexistent_task_has_empty_details(self, client: TestClient) -> None:
        """404 response must include details: {} (Requirement 1.3)."""
        fake_id = str(uuid4())
        response = client.post(f"/tasks/{fake_id}/complete")
        data = response.json()
        assert data.get("details") == {}

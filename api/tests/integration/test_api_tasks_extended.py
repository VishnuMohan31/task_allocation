from __future__ import annotations

import pytest


@pytest.fixture()
def created_task(client):
    resp = client.post("/tasks", json={"title": "Test task", "priority": 3})
    assert resp.status_code == 201
    return resp.json()


class TestListTasks:
    def test_returns_200(self, client):
        assert client.get("/tasks").status_code == 200

    def test_returns_empty_list_initially(self, client):
        assert client.get("/tasks").json() == []

    def test_returns_created_tasks(self, client, created_task):
        tasks = client.get("/tasks").json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == created_task["id"]

    def test_multiple_tasks_returned(self, client):
        client.post("/tasks", json={"title": "A", "priority": 1})
        client.post("/tasks", json={"title": "B", "priority": 2})
        assert len(client.get("/tasks").json()) == 2


class TestGetTask:
    def test_returns_200(self, client, created_task):
        assert client.get(f"/tasks/{created_task['id']}").status_code == 200

    def test_returns_correct_task(self, client, created_task):
        task = client.get(f"/tasks/{created_task['id']}").json()
        assert task["id"] == created_task["id"]
        assert task["title"] == created_task["title"]

    def test_not_found_returns_404(self, client):
        assert client.get("/tasks/nonexistent-id").status_code == 404

    def test_not_found_error_code(self, client):
        resp = client.get("/tasks/nonexistent-id").json()
        assert resp["error_code"] == "TASK_NOT_FOUND"


class TestUpdateTask:
    def test_returns_200(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"title": "Updated"})
        assert resp.status_code == 200

    def test_updates_title(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"title": "New title"})
        assert resp.json()["title"] == "New title"

    def test_updates_priority(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"priority": 5})
        assert resp.json()["priority"] == 5

    def test_updates_tags(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"tags": ["urgent"]})
        assert resp.json()["tags"] == ["urgent"]

    def test_partial_update_preserves_other_fields(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"priority": 5})
        assert resp.json()["title"] == created_task["title"]

    def test_not_found_returns_404(self, client):
        assert client.patch("/tasks/nonexistent-id", json={"title": "X"}).status_code == 404

    def test_empty_title_returns_422(self, client, created_task):
        assert client.patch(f"/tasks/{created_task['id']}", json={"title": ""}).status_code == 422

    def test_priority_out_of_range_returns_422(self, client, created_task):
        assert client.patch(f"/tasks/{created_task['id']}", json={"priority": 99}).status_code == 422


class TestDeleteTask:
    def test_returns_204(self, client, created_task):
        assert client.delete(f"/tasks/{created_task['id']}").status_code == 204

    def test_task_no_longer_exists_after_delete(self, client, created_task):
        client.delete(f"/tasks/{created_task['id']}")
        assert client.get(f"/tasks/{created_task['id']}").status_code == 404

    def test_not_found_returns_404(self, client):
        assert client.delete("/tasks/nonexistent-id").status_code == 404

    def test_not_found_error_code(self, client):
        resp = client.delete("/tasks/nonexistent-id").json()
        assert resp["error_code"] == "TASK_NOT_FOUND"


class TestCompleteTaskAlreadyCompleted:
    def test_already_completed_returns_409(self, client, created_task):
        client.post(f"/tasks/{created_task['id']}/complete")
        resp = client.post(f"/tasks/{created_task['id']}/complete")
        assert resp.status_code == 409

    def test_already_completed_error_code(self, client, created_task):
        client.post(f"/tasks/{created_task['id']}/complete")
        resp = client.post(f"/tasks/{created_task['id']}/complete").json()
        assert resp["error_code"] == "TASK_ALREADY_COMPLETED"


class TestDurationAndDeadlineFields:
    def test_create_with_duration_and_deadline(self, client):
        resp = client.post("/tasks/", json={
            "title": "Deploy service",
            "priority": 4,
            "duration_hours": 2.0,
            "deadline": "2026-03-25T18:00:00",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["duration_hours"] == 2.0
        assert "2026-03-25" in body["deadline"]

    def test_create_without_duration_and_deadline_defaults_to_null(self, client):
        resp = client.post("/tasks/", json={"title": "Simple task", "priority": 2})
        assert resp.status_code == 201
        body = resp.json()
        assert body["duration_hours"] is None
        assert body["deadline"] is None

    def test_create_with_fractional_hours(self, client):
        resp = client.post("/tasks/", json={"title": "Quick task", "priority": 2, "duration_hours": 0.5})
        assert resp.status_code == 201
        assert resp.json()["duration_hours"] == 0.5

    def test_update_sets_duration(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"duration_hours": 1.5})
        assert resp.status_code == 200
        assert resp.json()["duration_hours"] == 1.5

    def test_update_sets_deadline(self, client, created_task):
        resp = client.patch(f"/tasks/{created_task['id']}", json={"deadline": "2026-04-01T09:00:00"})
        assert resp.status_code == 200
        assert "2026-04-01" in resp.json()["deadline"]

    def test_duration_below_minimum_returns_422(self, client):
        resp = client.post("/tasks/", json={"title": "Bad task", "priority": 1, "duration_hours": 0.1})
        assert resp.status_code == 422

    def test_get_task_includes_duration_and_deadline(self, client):
        created = client.post("/tasks/", json={
            "title": "Review PR",
            "priority": 3,
            "duration_hours": 0.5,
            "deadline": "2026-03-24T17:00:00",
        }).json()
        fetched = client.get(f"/tasks/{created['id']}").json()
        assert fetched["duration_hours"] == 0.5
        assert "2026-03-24" in fetched["deadline"]

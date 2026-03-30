"""Core integration tests for the read-only tasks API.

Covers:
  - GET /tasks returns 200 with empty list
  - GET /tasks returns 200 with list of tasks
  - GET /tasks/{task_id} returns 200 with correct task
  - GET /tasks/{task_id} returns 404 for unknown ID
  - Response body does NOT contain is_deleted
  - POST/PATCH/DELETE return 404 or 405 (write endpoints removed)
"""
from __future__ import annotations

import pytest

from tests.integration.conftest import make_task_row


class TestListTasks:
    def test_empty_list(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row()]
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "TSK-001"
        assert data[0]["name"] == "Test Task"

    def test_response_excludes_is_deleted(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row()]
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert "is_deleted" not in resp.json()[0]


class TestGetTask:
    def test_returns_200_with_task(self, client, mock_pool):
        mock_pool.fetchrow.return_value = make_task_row(id="TSK-001")
        resp = client.get("/tasks/TSK-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "TSK-001"
        assert data["name"] == "Test Task"

    def test_returns_404_for_unknown_id(self, client, mock_pool):
        mock_pool.fetchrow.return_value = None
        resp = client.get("/tasks/UNKNOWN")
        assert resp.status_code == 404

    def test_response_excludes_is_deleted(self, client, mock_pool):
        mock_pool.fetchrow.return_value = make_task_row(id="TSK-001")
        resp = client.get("/tasks/TSK-001")
        assert resp.status_code == 200
        assert "is_deleted" not in resp.json()


class TestWriteEndpointsRemoved:
    def test_post_tasks_returns_404_or_405(self, client, mock_pool):
        resp = client.post("/tasks/", json={"name": "New Task"})
        assert resp.status_code in (404, 405)

    def test_patch_task_returns_404_or_405(self, client, mock_pool):
        resp = client.patch("/tasks/TSK-001", json={"name": "Updated"})
        assert resp.status_code in (404, 405)

    def test_delete_task_returns_404_or_405(self, client, mock_pool):
        resp = client.delete("/tasks/TSK-001")
        assert resp.status_code in (404, 405)

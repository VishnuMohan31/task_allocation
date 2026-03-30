"""Filter integration tests for GET /tasks query parameters.

Covers:
  - status, priority, sprint_id, assigned_to, phase_id filters
  - Multiple filters combined
"""
from __future__ import annotations

import pytest

from tests.integration.conftest import make_task_row


class TestFilterByStatus:
    def test_status_filter_returns_matching_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(status="Planning")]
        resp = client.get("/tasks/?status=Planning")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "Planning"

    def test_status_filter_returns_empty_when_no_match(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/?status=Done")
        assert resp.status_code == 200
        assert resp.json() == []


class TestFilterByPriority:
    def test_priority_filter_returns_matching_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(priority="High")]
        resp = client.get("/tasks/?priority=High")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["priority"] == "High"

    def test_priority_filter_returns_empty_when_no_match(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/?priority=Critical")
        assert resp.status_code == 200
        assert resp.json() == []


class TestFilterBySprintId:
    def test_sprint_id_filter_returns_matching_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(sprint_id="SP-001")]
        resp = client.get("/tasks/?sprint_id=SP-001")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["sprint_id"] == "SP-001"

    def test_sprint_id_filter_returns_empty_when_no_match(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/?sprint_id=SP-999")
        assert resp.status_code == 200
        assert resp.json() == []


class TestFilterByAssignedTo:
    def test_assigned_to_filter_returns_matching_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(assigned_to="user-1")]
        resp = client.get("/tasks/?assigned_to=user-1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["assigned_to"] == "user-1"

    def test_assigned_to_filter_returns_empty_when_no_match(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/?assigned_to=nobody")
        assert resp.status_code == 200
        assert resp.json() == []


class TestFilterByPhaseId:
    def test_phase_id_filter_returns_matching_tasks(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(phase_id="phase-1")]
        resp = client.get("/tasks/?phase_id=phase-1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["phase_id"] == "phase-1"

    def test_phase_id_filter_returns_empty_when_no_match(self, client, mock_pool):
        mock_pool.fetch.return_value = []
        resp = client.get("/tasks/?phase_id=phase-999")
        assert resp.status_code == 200
        assert resp.json() == []


class TestMultipleFilters:
    def test_status_and_priority_combined(self, client, mock_pool):
        mock_pool.fetch.return_value = [make_task_row(status="Planning", priority="High")]
        resp = client.get("/tasks/?status=Planning&priority=High")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "Planning"
        assert data[0]["priority"] == "High"

    def test_sprint_and_assigned_to_combined(self, client, mock_pool):
        mock_pool.fetch.return_value = [
            make_task_row(sprint_id="SP-001", assigned_to="user-1")
        ]
        resp = client.get("/tasks/?sprint_id=SP-001&assigned_to=user-1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["sprint_id"] == "SP-001"
        assert data[0]["assigned_to"] == "user-1"

    def test_all_filters_combined(self, client, mock_pool):
        mock_pool.fetch.return_value = [
            make_task_row(
                status="In Progress",
                priority="High",
                sprint_id="SP-002",
                assigned_to="user-2",
                phase_id="phase-1",
            )
        ]
        resp = client.get(
            "/tasks/?status=In Progress&priority=High&sprint_id=SP-002"
            "&assigned_to=user-2&phase_id=phase-1"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        task = data[0]
        assert task["status"] == "In Progress"
        assert task["priority"] == "High"
        assert task["sprint_id"] == "SP-002"
        assert task["assigned_to"] == "user-2"
        assert task["phase_id"] == "phase-1"

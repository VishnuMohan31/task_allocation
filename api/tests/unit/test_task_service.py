"""Tests for TaskService — core tests (task 8.2).

Covers:
  - list_tasks() with no filters delegates to repo and returns tasks
  - list_tasks(filters) passes filters through to repo
  - get_task(task_id) delegates to repo and returns the task
  - get_task(task_id) propagates TaskNotFoundError from repo
"""
from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from models.task import Task, TaskFilters
from services.task_service import TaskService
from utils.exceptions import TaskNotFoundError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=str(uuid4()),
        user_story_id=str(uuid4()),
        name="Sample task",
        status="Planning",
        priority="Medium",
    )
    defaults.update(kwargs)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def repo():
    mock = AsyncMock()
    return mock


@pytest.fixture()
def service(repo):
    return TaskService(repo=repo)


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    @pytest.mark.asyncio
    async def test_no_filters_delegates_to_repo(self, service, repo):
        """list_tasks() with no filters delegates to repo and returns tasks."""
        tasks = [_make_task(name="A"), _make_task(name="B")]
        repo.list_tasks.return_value = tasks

        result = await service.list_tasks()

        repo.list_tasks.assert_called_once_with(None)
        assert result == tasks

    @pytest.mark.asyncio
    async def test_filters_passed_through_to_repo(self, service, repo):
        """list_tasks(filters) passes filters through to repo."""
        filters = TaskFilters(status="In Progress", priority="High")
        tasks = [_make_task(name="Filtered")]
        repo.list_tasks.return_value = tasks

        result = await service.list_tasks(filters)

        repo.list_tasks.assert_called_once_with(filters)
        assert result == tasks


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

class TestGetTask:
    @pytest.mark.asyncio
    async def test_delegates_to_repo_and_returns_task(self, service, repo):
        """get_task(task_id) delegates to repo and returns the task."""
        task = _make_task(name="Find me")
        repo.get_task.return_value = task

        result = await service.get_task(task.id)

        repo.get_task.assert_called_once_with(task.id)
        assert result == task

    @pytest.mark.asyncio
    async def test_propagates_task_not_found_error(self, service, repo):
        """get_task(task_id) propagates TaskNotFoundError from repo."""
        repo.get_task.side_effect = TaskNotFoundError("nonexistent-id")

        with pytest.raises(TaskNotFoundError) as exc_info:
            await service.get_task("nonexistent-id")

        assert exc_info.value.task_id == "nonexistent-id"

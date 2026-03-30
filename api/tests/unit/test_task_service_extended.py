"""Extended tests for TaskService (task 8.2).

Covers:
  - list_tasks() returns empty list when repo returns empty
  - list_tasks() returns multiple tasks
  - get_task() returns correct task by id
  - Write operations (create_task, update_task, complete_task, delete_task)
    do NOT exist on TaskService
"""
from __future__ import annotations

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
        name="Task",
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
    return AsyncMock()


@pytest.fixture()
def service(repo):
    return TaskService(repo=repo)


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_repo_returns_empty(self, service, repo):
        """list_tasks() returns empty list when repo returns empty."""
        repo.list_tasks.return_value = []

        result = await service.list_tasks()

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_multiple_tasks(self, service, repo):
        """list_tasks() returns multiple tasks from repo."""
        tasks = [_make_task(name="Alpha"), _make_task(name="Beta"), _make_task(name="Gamma")]
        repo.list_tasks.return_value = tasks

        result = await service.list_tasks()

        assert len(result) == 3
        assert result == tasks


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

class TestGetTask:
    @pytest.mark.asyncio
    async def test_returns_correct_task_by_id(self, service, repo):
        """get_task() returns the correct task matching the given id."""
        task = _make_task(name="Specific task")
        repo.get_task.return_value = task

        result = await service.get_task(task.id)

        assert result.id == task.id
        assert result.name == "Specific task"


# ---------------------------------------------------------------------------
# Write operations must NOT exist on TaskService
# ---------------------------------------------------------------------------

class TestWriteOperationsDoNotExist:
    def test_create_task_does_not_exist(self, service):
        """create_task must NOT be a method on TaskService."""
        assert not hasattr(service, "create_task")

    def test_update_task_does_not_exist(self, service):
        """update_task must NOT be a method on TaskService."""
        assert not hasattr(service, "update_task")

    def test_complete_task_does_not_exist(self, service):
        """complete_task must NOT be a method on TaskService."""
        assert not hasattr(service, "complete_task")

    def test_delete_task_does_not_exist(self, service):
        """delete_task must NOT be a method on TaskService."""
        assert not hasattr(service, "delete_task")

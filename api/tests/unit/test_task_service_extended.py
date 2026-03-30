from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from models.task import Task, TaskUpdate
from services.task_service import TaskService
from utils.exceptions import TaskAlreadyCompletedError, TaskNotFoundError


def make_task(**kwargs) -> Task:
    defaults = dict(title="Task", description="", priority=3, completed=False, created_at=datetime.utcnow())
    return Task(**{**defaults, **kwargs})


@pytest.fixture()
def repo():
    return MagicMock()


@pytest.fixture()
def service(repo):
    return TaskService(repo=repo)


class TestListTasks:
    def test_returns_all_tasks(self, service, repo):
        tasks = [make_task(title="A"), make_task(title="B")]
        repo.list_tasks.return_value = tasks
        assert service.list_tasks() == tasks

    def test_returns_empty_list(self, service, repo):
        repo.list_tasks.return_value = []
        assert service.list_tasks() == []


class TestGetTask:
    def test_returns_task_by_id(self, service, repo):
        task = make_task(title="Find me")
        repo.get_task.return_value = task
        assert service.get_task(task.id) == task

    def test_raises_not_found(self, service, repo):
        repo.get_task.side_effect = TaskNotFoundError("missing-id")
        with pytest.raises(TaskNotFoundError):
            service.get_task("missing-id")


class TestUpdateTask:
    def test_updates_title(self, service, repo):
        task = make_task(title="Old title")
        updated = task.model_copy(update={"title": "New title"})
        repo.get_task.return_value = task
        repo.update_task.return_value = updated
        result = service.update_task(task.id, TaskUpdate(title="New title"))
        assert result.title == "New title"

    def test_updates_priority(self, service, repo):
        task = make_task(priority=2)
        updated = task.model_copy(update={"priority": 5})
        repo.get_task.return_value = task
        repo.update_task.return_value = updated
        result = service.update_task(task.id, TaskUpdate(priority=5))
        assert result.priority == 5

    def test_partial_update_ignores_none_fields(self, service, repo):
        task = make_task(title="Keep me", priority=3)
        repo.get_task.return_value = task
        repo.update_task.return_value = task
        service.update_task(task.id, TaskUpdate(priority=4))
        call_arg = repo.update_task.call_args[0][0]
        assert call_arg.title == "Keep me"

    def test_raises_not_found(self, service, repo):
        repo.get_task.side_effect = TaskNotFoundError("x")
        with pytest.raises(TaskNotFoundError):
            service.update_task("x", TaskUpdate(title="New"))


class TestCompleteTaskGuard:
    def test_raises_already_completed(self, service, repo):
        task = make_task(completed=True)
        repo.get_task.return_value = task
        with pytest.raises(TaskAlreadyCompletedError):
            service.complete_task(task.id)

    def test_does_not_call_update_when_already_completed(self, service, repo):
        task = make_task(completed=True)
        repo.get_task.return_value = task
        with pytest.raises(TaskAlreadyCompletedError):
            service.complete_task(task.id)
        repo.update_task.assert_not_called()


class TestDeleteTask:
    def test_calls_repo_delete(self, service, repo):
        service.delete_task("some-id")
        repo.delete_task.assert_called_once_with("some-id")

    def test_raises_not_found(self, service, repo):
        repo.delete_task.side_effect = TaskNotFoundError("x")
        with pytest.raises(TaskNotFoundError):
            service.delete_task("x")

"""Tests for TaskRepository — written TDD before implementation (task 5.1).

All tests use tmp_path and MUST NOT touch the real data/store.json.
"""
import json
from pathlib import Path

import pytest

from models.task import Task
from utils.exceptions import StoreCorruptedError, TaskNotFoundError


def make_task(**kwargs) -> Task:
    """Helper to create a Task with sensible defaults."""
    defaults = dict(
        title="Test task",
        description="",
        priority=3,
        tags=[],
        completed=False,
    )
    defaults.update(kwargs)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# Lazy import so tests can be collected even before the module exists
# ---------------------------------------------------------------------------

def get_repo(store_path: Path):
    from repositories.task_repository import TaskRepository  # noqa: PLC0415
    return TaskRepository(store_path)


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_returns_empty_list_when_store_does_not_exist(self, tmp_path):
        """Req 4.2 — list_tasks() must not raise when store.json is absent."""
        store = tmp_path / "store.json"
        repo = get_repo(store)
        result = repo.list_tasks()
        assert result == []

    def test_returns_all_tasks_when_store_exists(self, tmp_path):
        """list_tasks() returns every task persisted in the store."""
        store = tmp_path / "store.json"
        task1 = make_task(title="Task A", priority=1)
        task2 = make_task(title="Task B", priority=5)
        store.write_text(
            json.dumps([task1.model_dump(mode="json"), task2.model_dump(mode="json")])
        )
        repo = get_repo(store)
        result = repo.list_tasks()
        assert len(result) == 2
        ids = {t.id for t in result}
        assert task1.id in ids
        assert task2.id in ids

    def test_raises_store_corrupted_error_on_invalid_json(self, tmp_path):
        """Req 4.4 — invalid JSON must raise StoreCorruptedError."""
        store = tmp_path / "store.json"
        store.write_text("not valid json {{{{")
        repo = get_repo(store)
        with pytest.raises(StoreCorruptedError):
            repo.list_tasks()


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

class TestGetTask:
    def test_returns_correct_task_by_id(self, tmp_path):
        """get_task() returns the task matching the given ID."""
        store = tmp_path / "store.json"
        task = make_task(title="Find me")
        store.write_text(json.dumps([task.model_dump(mode="json")]))
        repo = get_repo(store)
        result = repo.get_task(task.id)
        assert result.id == task.id
        assert result.title == "Find me"

    def test_raises_task_not_found_when_id_missing(self, tmp_path):
        """Req 4.3 — get_task() must raise TaskNotFoundError for unknown IDs."""
        store = tmp_path / "store.json"
        store.write_text(json.dumps([]))
        repo = get_repo(store)
        with pytest.raises(TaskNotFoundError):
            repo.get_task("nonexistent-id")

    def test_raises_store_corrupted_error_on_invalid_json(self, tmp_path):
        """Req 4.4 — invalid JSON must raise StoreCorruptedError."""
        store = tmp_path / "store.json"
        store.write_text("{bad json")
        repo = get_repo(store)
        with pytest.raises(StoreCorruptedError):
            repo.get_task("any-id")


# ---------------------------------------------------------------------------
# save_task
# ---------------------------------------------------------------------------

class TestSaveTask:
    def test_persists_new_task_and_returns_it(self, tmp_path):
        """save_task() writes the task to the store and returns it."""
        store = tmp_path / "store.json"
        store.write_text(json.dumps([]))
        repo = get_repo(store)
        task = make_task(title="Persisted")
        returned = repo.save_task(task)
        assert returned.id == task.id
        # Verify it's actually on disk
        data = json.loads(store.read_text())
        assert any(t["id"] == task.id for t in data)

    def test_creates_store_file_if_not_exists(self, tmp_path):
        """save_task() must create store.json when it doesn't exist yet."""
        store = tmp_path / "store.json"
        assert not store.exists()
        repo = get_repo(store)
        task = make_task(title="Bootstrap")
        repo.save_task(task)
        assert store.exists()
        data = json.loads(store.read_text())
        assert len(data) == 1
        assert data[0]["id"] == task.id

    def test_raises_store_corrupted_error_on_invalid_json(self, tmp_path):
        """Req 4.4 — invalid JSON must raise StoreCorruptedError."""
        store = tmp_path / "store.json"
        store.write_text("!!!invalid!!!")
        repo = get_repo(store)
        with pytest.raises(StoreCorruptedError):
            repo.save_task(make_task())


# ---------------------------------------------------------------------------
# update_task
# ---------------------------------------------------------------------------

class TestUpdateTask:
    def test_updates_existing_task_and_returns_it(self, tmp_path):
        """update_task() replaces the stored task and returns the updated version."""
        store = tmp_path / "store.json"
        task = make_task(title="Original")
        store.write_text(json.dumps([task.model_dump(mode="json")]))
        repo = get_repo(store)
        updated = task.model_copy(update={"title": "Updated", "completed": True})
        returned = repo.update_task(updated)
        assert returned.title == "Updated"
        assert returned.completed is True
        # Verify persistence
        data = json.loads(store.read_text())
        assert data[0]["title"] == "Updated"

    def test_raises_task_not_found_when_id_missing(self, tmp_path):
        """update_task() must raise TaskNotFoundError when the task doesn't exist."""
        store = tmp_path / "store.json"
        store.write_text(json.dumps([]))
        repo = get_repo(store)
        ghost = make_task(title="Ghost")
        with pytest.raises(TaskNotFoundError):
            repo.update_task(ghost)

    def test_raises_store_corrupted_error_on_invalid_json(self, tmp_path):
        """Req 4.4 — invalid JSON must raise StoreCorruptedError."""
        store = tmp_path / "store.json"
        store.write_text("corrupted")
        repo = get_repo(store)
        with pytest.raises(StoreCorruptedError):
            repo.update_task(make_task())

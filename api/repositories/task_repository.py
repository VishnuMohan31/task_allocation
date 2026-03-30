"""File-based JSON task repository with atomic read-modify-write."""
import json
from pathlib import Path

from models.task import Task
from utils.exceptions import StoreCorruptedError, TaskNotFoundError


class TaskRepository:
    def __init__(self, store_path: Path) -> None:
        self._store_path = store_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read(self) -> list[dict]:
        """Read raw task dicts from disk. Returns [] if file absent."""
        if not self._store_path.exists():
            return []
        try:
            return json.loads(self._store_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise StoreCorruptedError() from exc

    def _write(self, tasks: list[Task]) -> None:
        """Serialize and write tasks to disk."""
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            json.dumps([t.model_dump(mode="json") for t in tasks], indent=2),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_tasks(self) -> list[Task]:
        """Return all tasks. Returns [] when store does not exist (Req 4.2)."""
        return [Task(**raw) for raw in self._read()]

    def get_task(self, task_id: str) -> Task:
        """Return task by ID. Raises TaskNotFoundError if absent (Req 4.3)."""
        for raw in self._read():
            if raw.get("id") == task_id:
                return Task(**raw)
        raise TaskNotFoundError(task_id)

    def save_task(self, task: Task) -> Task:
        """Append a new task to the store. Creates the file if needed."""
        tasks = [Task(**raw) for raw in self._read()]
        tasks.append(task)
        self._write(tasks)
        return task

    def update_task(self, task: Task) -> Task:
        """Replace an existing task in-place. Raises TaskNotFoundError if absent."""
        raws = self._read()
        for i, raw in enumerate(raws):
            if raw.get("id") == task.id:
                raws[i] = task.model_dump(mode="json")
                self._store_path.write_text(
                    json.dumps(raws, indent=2), encoding="utf-8"
                )
                return task
        raise TaskNotFoundError(task.id)

    def delete_task(self, task_id: str) -> None:
        """Remove a task by ID. Raises TaskNotFoundError if absent."""
        raws = self._read()
        new_raws = [r for r in raws if r.get("id") != task_id]
        if len(new_raws) == len(raws):
            raise TaskNotFoundError(task_id)
        self._store_path.write_text(
            json.dumps(new_raws, indent=2), encoding="utf-8"
        )

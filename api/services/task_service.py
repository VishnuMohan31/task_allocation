from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from models.task import Task, TaskCreate, TaskUpdate
from repositories.task_repository import TaskRepository
from utils.exceptions import TaskAlreadyCompletedError


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def list_tasks(self) -> list[Task]:
        return self._repo.list_tasks()

    def get_task(self, task_id: str) -> Task:
        return self._repo.get_task(task_id)

    def create_task(self, task_in: TaskCreate) -> Task:
        task = Task(
            id=str(uuid4()),
            title=task_in.title,
            description=task_in.description,
            priority=task_in.priority,
            tags=task_in.tags,
            duration_hours=task_in.duration_hours,
            deadline=task_in.deadline,
            completed=False,
            created_at=datetime.utcnow(),
            completed_at=None,
        )
        return self._repo.save_task(task)

    def update_task(self, task_id: str, task_in: TaskUpdate) -> Task:
        task = self._repo.get_task(task_id)
        updates = task_in.model_dump(exclude_none=True)
        updated = task.model_copy(update=updates)
        return self._repo.update_task(updated)

    def complete_task(self, task_id: str) -> Task:
        task = self._repo.get_task(task_id)
        if task.completed:
            raise TaskAlreadyCompletedError(task_id)
        updated = task.model_copy(update={"completed": True, "completed_at": datetime.utcnow()})
        return self._repo.update_task(updated)

    def delete_task(self, task_id: str) -> None:
        self._repo.delete_task(task_id)

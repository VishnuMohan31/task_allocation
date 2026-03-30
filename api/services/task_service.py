from __future__ import annotations

from models.task import Task, TaskFilters
from repositories.task_repository import PostgresTaskRepository


class TaskService:
    def __init__(self, repo: PostgresTaskRepository) -> None:
        self._repo = repo

    async def list_tasks(self, filters: TaskFilters | None = None) -> list[Task]:
        return await self._repo.list_tasks(filters)

    async def get_task(self, task_id: str) -> Task:
        return await self._repo.get_task(task_id)

from __future__ import annotations

from fastapi import APIRouter

from core.config import settings
from models.task import TaskFilters, TaskResponse
from repositories.task_repository import PostgresTaskRepository
from services.task_service import TaskService

router = APIRouter(prefix=settings.tasks_prefix, tags=[settings.tasks_tag])

# Module-level singleton — pool is initialised via lifespan in main.py
_repo = PostgresTaskRepository(settings)
_service = TaskService(repo=_repo)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    sprint_id: str | None = None,
    assigned_to: str | None = None,
    phase_id: str | None = None,
) -> list[TaskResponse]:
    filters = TaskFilters(
        status=status,
        priority=priority,
        sprint_id=sprint_id,
        assigned_to=assigned_to,
        phase_id=phase_id,
    )
    tasks = await _service.list_tasks(filters)
    return [TaskResponse(**t.model_dump(exclude={"is_deleted"})) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    task = await _service.get_task(task_id)
    return TaskResponse(**task.model_dump(exclude={"is_deleted"}))

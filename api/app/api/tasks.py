from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from core.config import settings
from models.task import TaskCreate, TaskResponse, TaskUpdate
from repositories.task_repository import TaskRepository
from services.task_service import TaskService

router = APIRouter(prefix=settings.tasks_prefix, tags=[settings.tasks_tag])


def get_repository() -> TaskRepository:
    return TaskRepository(store_path=settings.store_path)


def get_service(repo: TaskRepository = Depends(get_repository)) -> TaskService:
    return TaskService(repo=repo)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(service: TaskService = Depends(get_service)) -> list[TaskResponse]:
    return [TaskResponse(**t.model_dump()) for t in service.list_tasks()]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, service: TaskService = Depends(get_service)) -> TaskResponse:
    task = service.get_task(task_id)
    return TaskResponse(**task.model_dump())


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_service),
) -> TaskResponse:
    task = service.create_task(task_in)
    return TaskResponse(**task.model_dump())


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_service),
) -> TaskResponse:
    task = service.update_task(task_id, task_in)
    return TaskResponse(**task.model_dump())


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    service: TaskService = Depends(get_service),
) -> TaskResponse:
    task = service.complete_task(task_id)
    return TaskResponse(**task.model_dump())


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_service),
) -> Response:
    service.delete_task(task_id)
    return Response(status_code=204)

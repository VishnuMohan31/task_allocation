from __future__ import annotations

from fastapi import APIRouter, Depends

from core.config import settings
from models.agent import AgentDecision
from repositories.task_repository import TaskRepository
from services.agent_service import decide

router = APIRouter(prefix=settings.agent_prefix, tags=[settings.agent_tag])


def get_repository() -> TaskRepository:
    return TaskRepository(store_path=settings.store_path)


@router.get(settings.agent_decision_path, response_model=AgentDecision)
async def get_decision(
    repo: TaskRepository = Depends(get_repository),
) -> AgentDecision:
    tasks = repo.list_tasks()
    return decide(tasks)

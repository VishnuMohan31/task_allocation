from __future__ import annotations

from fastapi import APIRouter

from app.api.tasks import _service
from core.config import settings
from models.agent import AgentDecision
from services.agent_service import decide

router = APIRouter(prefix=settings.agent_prefix, tags=[settings.agent_tag])


@router.get(settings.agent_decision_path, response_model=AgentDecision)
async def get_decision() -> AgentDecision:
    return await decide(_service)

from __future__ import annotations

from pydantic import BaseModel

from models.task import Task


class AgentDecision(BaseModel):
    next_task: Task | None
    productivity_score: float  # 0.0 – 1.0
    suggestion: str
    reasoning: str = ""  # agent's explanation of why it made this decision


class AgentDecisionResponse(BaseModel):
    data: AgentDecision

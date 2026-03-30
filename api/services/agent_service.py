from __future__ import annotations

import json

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from core.config import settings
from models.agent import AgentDecision
from models.task import Task


@tool
def get_pending_tasks(tasks_json: str) -> str:
    """Return all pending (incomplete) tasks from the provided JSON task list."""
    tasks = [Task(**t) for t in json.loads(tasks_json)]
    pending = [t for t in tasks if not t.completed]
    if not pending:
        return settings.agent_no_pending_message
    return json.dumps([
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "duration_hours": t.duration_hours,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "created_at": t.created_at.isoformat(),
        }
        for t in pending
    ])


@tool
def calculate_productivity_score(tasks_json: str) -> str:
    """Calculate a weighted productivity score (0.0-1.0) from the task list."""
    tasks = [Task(**t) for t in json.loads(tasks_json)]
    if not tasks:
        return str(0.0)
    weighted_total = sum(t.priority for t in tasks)
    if weighted_total == 0:
        return str(0.0)
    weighted_done = sum(t.priority for t in tasks if t.completed)
    return str(round(weighted_done / weighted_total, 4))


def _build_agent():
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.openai_temperature,
    )
    return create_react_agent(llm, [get_pending_tasks, calculate_productivity_score])


def decide(tasks: list[Task]) -> AgentDecision:
    tasks_json = json.dumps([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "tags": t.tags,
            "duration_hours": t.duration_hours,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "completed": t.completed,
            "created_at": t.created_at.isoformat(),
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in tasks
    ])

    agent = _build_agent()
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": settings.agent_system_prompt},
            {"role": "user", "content": settings.agent_user_prompt_template.format(tasks_json=tasks_json)},
        ]
    })

    output = result["messages"][-1].content
    decision_data = json.loads(output)

    next_task_id = decision_data.get("next_task_id")
    next_task = next((t for t in tasks if t.id == next_task_id), None) if next_task_id else None

    return AgentDecision(
        next_task=next_task,
        productivity_score=float(decision_data.get("productivity_score", 0.0)),
        suggestion=decision_data.get("suggestion", ""),
        reasoning=decision_data.get("reasoning", ""),
    )

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
    """Return all non-completed tasks from the provided JSON task list."""
    tasks_data = json.loads(tasks_json)
    if not tasks_data:
        return settings.agent_no_pending_message
    return json.dumps([
        {
            "id": t["id"],
            "name": t["name"],
            "status": t["status"],
            "priority": t["priority"],
        }
        for t in tasks_data
    ])


@tool
def calculate_productivity_score(tasks_json: str) -> str:
    """Calculate a productivity score (0.0-1.0) from the task list."""
    tasks_data = json.loads(tasks_json)
    if not tasks_data:
        return str(0.0)
    total = len(tasks_data)
    done = sum(1 for t in tasks_data if t.get("status") == "Done")
    return str(round(done / total, 4))


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
            "name": t.name,
            "status": t.status,
            "priority": t.priority,
            "sprint_id": t.sprint_id,
            "assigned_to": t.assigned_to,
            "phase_id": t.phase_id,
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

"""LangGraph Studio entrypoint (see langgraph.json).

Run from api/:
  pip install -r requirements-dev.txt
  langgraph dev --allow-blocking

``--allow-blocking`` avoids BlockingError from LangGraph's detector when dependencies
(e.g. OpenAI/tiktoken) call sync OS APIs like os.getcwd() inside async runs — normal for local dev.

Requires DB env vars; pool is created on first query if the API lifespan did not run.
"""
from __future__ import annotations

from app.api.tasks import _service
from services.agent_service import build_agent_graph

graph = build_agent_graph(_service)

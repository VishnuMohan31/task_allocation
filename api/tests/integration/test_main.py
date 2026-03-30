"""Tests that app/main.py wires up routers, middleware, and exception handlers."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

from app.main import app
from app.middleware import LoggingMiddleware


def _route_paths() -> set[str]:
    return {route.path for route in app.routes}  # type: ignore[attr-defined]


def test_tasks_list_route_registered() -> None:
    assert "/tasks/" in _route_paths()


def test_tasks_get_route_registered() -> None:
    assert "/tasks/{task_id}" in _route_paths()


def test_agent_decision_route_registered() -> None:
    assert "/agent/decision" in _route_paths()


def test_logging_middleware_registered() -> None:
    middleware_classes = [m.cls for m in app.user_middleware]
    assert LoggingMiddleware in middleware_classes

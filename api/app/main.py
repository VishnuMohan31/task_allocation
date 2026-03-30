"""FastAPI application entry point."""
from __future__ import annotations

import contextlib
import sys
from pathlib import Path

# Ensure the api/ directory is on sys.path so imports work when running
# this file directly with: python app/main.py
_api_dir = Path(__file__).resolve().parent.parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.api.tasks import router as tasks_router, _repo
from app.middleware import LoggingMiddleware
from core.config import settings
from utils.error_handlers import register_exception_handlers


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await _repo.init_pool()
    yield
    await _repo.close_pool()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.add_middleware(LoggingMiddleware)

app.include_router(tasks_router)
app.include_router(agent_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )

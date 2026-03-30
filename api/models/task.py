from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from core.config import settings


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=settings.task_title_max_length)
    description: str = ""
    priority: int = Field(..., ge=settings.task_priority_min, le=settings.task_priority_max)
    tags: list[str] = []
    duration_hours: float | None = Field(None, ge=settings.task_duration_min)
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(settings.task_title_empty_error)
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=settings.task_title_max_length)
    description: str | None = None
    priority: int | None = Field(None, ge=settings.task_priority_min, le=settings.task_priority_max)
    tags: list[str] | None = None
    duration_hours: float | None = Field(None, ge=settings.task_duration_min)
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError(settings.task_title_empty_error)
        return v.strip() if v else v


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    priority: int = Field(..., ge=settings.task_priority_min, le=settings.task_priority_max)
    tags: list[str] = []
    duration_hours: float | None = None  # estimated effort in hours
    deadline: datetime | None = None     # hard deadline (UTC)
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: int
    tags: list[str]
    duration_hours: float | None = None
    deadline: datetime | None = None
    completed: bool
    created_at: datetime
    completed_at: datetime | None = None

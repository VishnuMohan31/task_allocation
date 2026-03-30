from datetime import date, datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    user_story_id: str
    name: str
    short_description: str | None = None
    long_description: str | None = None
    phase_id: str | None = None
    status: str = "Planning"
    priority: str = "Medium"
    assigned_to: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    start_date: date | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    sprint_id: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None


class TaskResponse(BaseModel):
    id: str
    user_story_id: str
    name: str
    short_description: str | None = None
    long_description: str | None = None
    phase_id: str | None = None
    status: str
    priority: str
    assigned_to: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    start_date: date | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    sprint_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None


class TaskFilters(BaseModel):
    status: str | None = None
    priority: str | None = None
    sprint_id: str | None = None
    assigned_to: str | None = None
    phase_id: str | None = None

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class Task(BaseModel):
    id: str
    spec_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    parallel: bool = False
    depends_on: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    acceptance: str = ""


class TaskList(BaseModel):
    spec_id: str
    tasks: list[Task] = Field(default_factory=list)

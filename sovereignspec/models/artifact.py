from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    CODE = "code"
    TEST = "test"
    DOC = "doc"
    CONFIG = "config"
    MIGRATION = "migration"
    OTHER = "other"


class ArtifactRecord(BaseModel):
    id: str
    task_id: str
    artifact_type: ArtifactType
    file_path: str
    validated: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ArtifactRegistry(BaseModel):
    agent: str
    project: str = ""
    artifacts: list[ArtifactRecord] = Field(default_factory=list)

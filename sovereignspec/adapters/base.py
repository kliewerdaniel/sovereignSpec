from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class AgentAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        ...

    @abstractmethod
    def generate_command_templates(self) -> dict[str, str]:
        ...

    def artifact_path(self, project_dir: str | Path, agent_name: str) -> str:
        return str(Path(project_dir) / ".sovereignspec" / "agents" / agent_name / "artifacts.json")

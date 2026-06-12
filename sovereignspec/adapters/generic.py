from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class GenericFilesystemAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "generic"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        return []

    def generate_command_templates(self) -> dict[str, str]:
        return {}

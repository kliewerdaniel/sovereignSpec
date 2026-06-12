from __future__ import annotations

from pathlib import Path

import yaml

from sovereignspec.adapters.base import AgentAdapter


class AiderAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "aider"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        config_file = base / ".aider.conf.yml"
        config_file.write_text(self._config_content())
        return [str(config_file)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _config_content(self) -> str:
        config = {
            "auto-commits": False,
            "lint": True,
            "test": True,
            "chat-mode": "architect",
            "map-refresh": "manual",
            "git": False,
        }
        return yaml.dump(config, default_flow_style=False)

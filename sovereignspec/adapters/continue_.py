from __future__ import annotations

import json
from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class ContinueAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "continue"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        continue_dir = base / ".continue"
        continue_dir.mkdir(parents=True, exist_ok=True)

        commands_dir = continue_dir / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        files_written: list[str] = []

        config_file = continue_dir / "config.json"
        config_file.write_text(self._config_content())
        files_written.append(str(config_file))

        for cmd_name in ["sovereign-constitution", "sovereign-specify", "sovereign-clarify",
                          "sovereign-plan", "sovereign-tasks", "sovereign-analyze",
                          "sovereign-implement", "sovereign-checklist"]:
            cmd_file = commands_dir / f"{cmd_name}.json"
            cmd_file.write_text(json.dumps({"name": cmd_name, "description": f"Run {cmd_name}"}, indent=2))
            files_written.append(str(cmd_file))

        return files_written

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _config_content(self) -> str:
        config = {
            "name": "SovereignSpec",
            "version": "1.0.0",
            "experimental": {
                "slashCommands": True,
                "naturalLanguageCommands": True,
            },
            "slashCommands": [
                {"name": "sovereign-constitution", "description": "Generate or update project constitution"},
                {"name": "sovereign-specify", "description": "Define a new feature spec"},
                {"name": "sovereign-clarify", "description": "Get RAG-grounded clarification"},
                {"name": "sovereign-plan", "description": "Generate implementation plan"},
                {"name": "sovereign-tasks", "description": "Decompose plan into tasks"},
                {"name": "sovereign-analyze", "description": "Check contradictions and drift"},
                {"name": "sovereign-implement", "description": "Execute implementation"},
                {"name": "sovereign-checklist", "description": "Verify quality"},
            ],
        }
        return json.dumps(config, indent=2)

from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class WindsurfAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "windsurf"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        rules_file = base / ".windsurfrules"
        rules_file.write_text(self._rules_content())
        return [str(rules_file)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _rules_content(self) -> str:
        return """# SovereignSpec — Windsurf Integration

This project uses SovereignSpec for spec-driven development.

## Required Reading
- .sovereignspec/constitution.md
- .sovereignspec/specs/
- .sovereignspec/adr/
- .sovereignspec/tasks/active_tasks.md
- .sovereignspec/patterns/pattern_library.json

## Rules
- Honor all spec constraints
- Generate tests for every feature
- Update task status on completion
- Register artifacts after implementation
- Do not modify .sspec files
"""

from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class ClineAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "cline"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        clinerules = base / ".clinerules"
        clinerules.write_text(self._clinerules_content())
        return [str(clinerules)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _clinerules_content(self) -> str:
        return """# SovereignSpec — Cline Integration

This project uses SovereignSpec for spec-driven development.

## Required Reading
1. .sovereignspec/constitution.md
2. .sovereignspec/specs/ (all .sspec files)
3. .sovereignspec/adr/ (architecture decisions)
4. .sovereignspec/tasks/active_tasks.md
5. .sovereignspec/patterns/pattern_library.json

## Rules
- Honor all spec constraints
- Generate tests for every implementation
- Update task status on completion
- Register artifacts after implementation
- Never modify .sspec files
"""

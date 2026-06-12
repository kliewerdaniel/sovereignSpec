from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class RooCodeAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "roocode"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        rules_dir = base / ".roo"
        rules_dir.mkdir(parents=True, exist_ok=True)

        rules_file = rules_dir / "rules.md"
        rules_file.write_text(self._rules_content())
        return [str(rules_file)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _rules_content(self) -> str:
        return """# SovereignSpec — RooCode Integration

This project uses SovereignSpec for spec-driven development.

## Required Reading
1. `.sovereignspec/constitution.md`
2. `.sovereignspec/specs/`
3. `.sovereignspec/adr/`
4. `.sovereignspec/tasks/active_tasks.md`
5. `.sovereignspec/patterns/pattern_library.json`

## Rules
- Honor all constraints in active specs
- Generate tests for every feature
- Update task status upon completion
- Register artifacts after implementation
- Do not modify .sspec files
"""

from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class CursorAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "cursor"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        rules_dir = base / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        rule_file = rules_dir / "sovereignspec.mdc"
        rule_file.write_text(self._rule_content())
        return [str(rule_file)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _rule_content(self) -> str:
        return """---
description: SovereignSpec Spec-Driven Development rules for this project
---

# SovereignSpec Rules

This project uses SovereignSpec for spec-driven development.

## Before implementing
- Read `.sovereignspec/constitution.md`
- Read active specs in `.sovereignspec/specs/`
- Read ADRs in `.sovereignspec/adr/`
- Read `.sovereignspec/tasks/active_tasks.md`
- Read `.sovereignspec/patterns/pattern_library.json`

## Requirements
- Honor all constraints in active specs
- Generate tests for every feature
- Update task status on completion
- Register artifacts after implementation
- Do not modify .sspec files
"""

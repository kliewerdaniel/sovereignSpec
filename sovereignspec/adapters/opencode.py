from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class OpenCodeAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "opencode"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        agents_md = base / "AGENTS.md"
        content = self._agents_md_content()
        agents_md.write_text(content)
        return [str(agents_md)]

    def generate_command_templates(self) -> dict[str, str]:
        return {
            "sovereign-constitution": "Generate or update the project constitution.",
            "sovereign-specify": "Create a new .sspec specification file from a description.",
            "sovereign-clarify": "Answer questions about a spec using RAG-grounded context.",
            "sovereign-plan": "Generate a technical implementation plan for a spec.",
            "sovereign-tasks": "Decompose a spec into actionable tasks.",
            "sovereign-analyze": "Check specs for contradictions and narrative drift.",
            "sovereign-implement": "Execute implementation against spec constraints.",
            "sovereign-checklist": "Verify implementation quality against acceptance criteria.",
        }

    def _agents_md_content(self) -> str:
        return """# SovereignSpec — OpenCode Integration

This project uses SovereignSpec for spec-driven development.

## Contract
Before writing any code, read:
- `.sovereignspec/constitution.md`
- `.sovereignspec/specs/` (all active specs)
- `.sovereignspec/adr/` (architecture decisions)
- `.sovereignspec/tasks/active_tasks.md`
- `.sovereignspec/patterns/pattern_library.json`

## Rules
- Honor all constraints in active specs
- Generate tests for every feature
- Update task status on completion
- Register artifacts after implementation
- Do not modify .sspec files

## Commands
/sovereign-constitution
/sovereign-specify
/sovereign-clarify
/sovereign-plan
/sovereign-tasks
/sovereign-analyze
/sovereign-implement
/sovereign-checklist
"""

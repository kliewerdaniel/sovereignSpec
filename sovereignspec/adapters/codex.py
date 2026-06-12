from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class CodexAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "codex"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        files_written: list[str] = []

        agents_md = base / "AGENTS.md"
        agents_md.write_text(self._agents_md_content())
        files_written.append(str(agents_md))

        skills_dir = base / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        sovereign_file = skills_dir / "sovereignspec.md"
        sovereign_file.write_text(self._skill_content())
        files_written.append(str(sovereign_file))

        return files_written

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _agents_md_content(self) -> str:
        return """# SovereignSpec — Codex CLI Integration

This project uses SovereignSpec for spec-driven development.

## Contract
Before implementing:
- Read `.sovereignspec/constitution.md`
- Read `.sovereignspec/specs/` for active specs
- Read `.sovereignspec/adr/` for architecture decisions
- Read `.sovereignspec/tasks/active_tasks.md`
- Read `.sovereignspec/patterns/pattern_library.json`

## Rules
- Honor all spec constraints
- Generate tests for every feature
- Update task status on completion
- Register artifacts after implementation
- Never modify .sspec files
"""

    def _skill_content(self) -> str:
        return """# SovereignSpec Skill

Spec-Driven Development skill for this project.

## Available Commands
- `/sovereign.specify` — Define a new feature spec
- `/sovereign.clarify` — Get RAG-grounded clarification
- `/sovereign.plan` — Generate implementation plan
- `/sovereign.tasks` — Decompose into tasks
- `/sovereign.implement` — Execute implementation
"""

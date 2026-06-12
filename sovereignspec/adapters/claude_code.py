from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class ClaudeCodeAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "claude-code"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        commands_dir = base / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        files_written: list[str] = []

        claude_md = base / "CLAUDE.md"
        claude_md.write_text(self._claude_md_content())
        files_written.append(str(claude_md))

        commands = {
            "sovereign-constitution.md": self._cmd_constitution(),
            "sovereign-specify.md": self._cmd_specify(),
            "sovereign-clarify.md": self._cmd_clarify(),
            "sovereign-plan.md": self._cmd_plan(),
            "sovereign-tasks.md": self._cmd_tasks(),
            "sovereign-analyze.md": self._cmd_analyze(),
            "sovereign-implement.md": self._cmd_implement(),
            "sovereign-checklist.md": self._cmd_checklist(),
        }

        for filename, content in commands.items():
            path = commands_dir / filename
            path.write_text(content)
            files_written.append(str(path))

        return files_written

    def generate_command_templates(self) -> dict[str, str]:
        return {
            "sovereign-constitution": self._cmd_constitution(),
            "sovereign-specify": self._cmd_specify(),
            "sovereign-clarify": self._cmd_clarify(),
            "sovereign-plan": self._cmd_plan(),
            "sovereign-tasks": self._cmd_tasks(),
            "sovereign-analyze": self._cmd_analyze(),
            "sovereign-implement": self._cmd_implement(),
            "sovereign-checklist": self._cmd_checklist(),
        }

    def _claude_md_content(self) -> str:
        return """# SovereignSpec — Claude Code Integration

This project uses SovereignSpec for spec-driven development.

## Required Reading
Before implementing anything, read:
1. `.sovereignspec/constitution.md` — Project governing principles
2. `.sovereignspec/specs/` — Active specification files
3. `.sovereignspec/adr/` — Architecture Decision Records
4. `.sovereignspec/tasks/active_tasks.md` — Current work units
5. `.sovereignspec/patterns/pattern_library.json` — Coding conventions

## Available Commands
Use `/sovereign-constitution` to establish project governing principles.
Use `/sovereign-specify` to define a new feature spec.
Use `/sovereign-clarify` to get RAG-grounded clarification of a spec.
Use `/sovereign-plan` to generate implementation plan.
Use `/sovereign-tasks` to decompose plan into tasks.
Use `/sovereign-analyze` to check contradictions and drift.
Use `/sovereign-implement` to execute implementation.
Use `/sovereign-checklist` to verify quality.

## Key Rules
- Do not modify .sspec files
- Generate tests for every implemented feature
- Honor all constraints listed in active specs
- Update task status upon completion
- Register artifacts after implementation
"""

    def _cmd_constitution(self) -> str:
        return "Generate or update the project constitution based on the provided description."

    def _cmd_specify(self) -> str:
        return "Create a new .sspec specification file from a feature description."

    def _cmd_clarify(self) -> str:
        return "Answer questions about a spec using RAG-grounded context."

    def _cmd_plan(self) -> str:
        return "Generate a technical implementation plan for a spec."

    def _cmd_tasks(self) -> str:
        return "Decompose a spec into actionable implementation tasks."

    def _cmd_analyze(self) -> str:
        return "Check specs for contradictions and narrative drift."

    def _cmd_implement(self) -> str:
        return "Execute implementation tasks against spec constraints."

    def _cmd_checklist(self) -> str:
        return "Verify implementation quality against acceptance criteria."

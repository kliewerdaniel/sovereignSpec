from __future__ import annotations

from pathlib import Path

from sovereignspec.adapters.base import AgentAdapter


class GeminiCLIAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "gemini-cli"

    def write_integration_files(self, project_dir: str | Path) -> list[str]:
        base = Path(project_dir)
        gemini_md = base / "GEMINI.md"
        gemini_md.write_text(self._gemini_md_content())
        return [str(gemini_md)]

    def generate_command_templates(self) -> dict[str, str]:
        return {}

    def _gemini_md_content(self) -> str:
        return """# SovereignSpec — Gemini CLI Integration

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

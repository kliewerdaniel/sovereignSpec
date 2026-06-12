from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from sovereignspec.adapters import get_adapter


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    return tmp_path


class TestAgentIntegration:
    def test_claude_code_writes_claude_md(self, temp_project: Path) -> None:
        adapter = get_adapter("claude-code")
        files = adapter.write_integration_files(temp_project)
        assert any(Path(f).name == "CLAUDE.md" for f in files)

    def test_claude_code_writes_commands(self, temp_project: Path) -> None:
        adapter = get_adapter("claude-code")
        files = adapter.write_integration_files(temp_project)
        command_files = [f for f in files if ".claude/commands" in f]
        assert len(command_files) >= 7

    def test_opencode_writes_agents_md(self, temp_project: Path) -> None:
        adapter = get_adapter("opencode")
        files = adapter.write_integration_files(temp_project)
        assert any("AGENTS.md" in str(Path(f).name) for f in files)

    def test_cursor_writes_rule_file(self, temp_project: Path) -> None:
        adapter = get_adapter("cursor")
        files = adapter.write_integration_files(temp_project)
        assert any(f.endswith(".mdc") for f in files)

    def test_cline_writes_clinerules(self, temp_project: Path) -> None:
        adapter = get_adapter("cline")
        files = adapter.write_integration_files(temp_project)
        assert any(f.endswith(".clinerules") for f in files)

    def test_roocode_writes_rules(self, temp_project: Path) -> None:
        adapter = get_adapter("roocode")
        files = adapter.write_integration_files(temp_project)
        assert any(f.endswith("rules.md") for f in files)

    def test_codex_writes_agents_md_and_skills(self, temp_project: Path) -> None:
        adapter = get_adapter("codex")
        files = adapter.write_integration_files(temp_project)
        assert any("AGENTS.md" in f for f in files)
        assert any("skills" in f for f in files)

    def test_gemini_cli_writes_gemini_md(self, temp_project: Path) -> None:
        adapter = get_adapter("gemini-cli")
        files = adapter.write_integration_files(temp_project)
        assert any("GEMINI.md" in f for f in files)

    def test_aider_writes_config(self, temp_project: Path) -> None:
        adapter = get_adapter("aider")
        files = adapter.write_integration_files(temp_project)
        assert any(f.endswith(".aider.conf.yml") for f in files)

    def test_windsurf_writes_rules(self, temp_project: Path) -> None:
        adapter = get_adapter("windsurf")
        files = adapter.write_integration_files(temp_project)
        assert any(f.endswith(".windsurfrules") for f in files)

    def test_continue_writes_config_and_commands(self, temp_project: Path) -> None:
        adapter = get_adapter("continue")
        files = adapter.write_integration_files(temp_project)
        config_files = [f for f in files if "config.json" in f]
        command_files = [f for f in files if "commands" in f]
        assert len(config_files) >= 1
        assert len(command_files) >= 1

    def test_generic_writes_nothing(self, temp_project: Path) -> None:
        adapter = get_adapter("generic")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 0

    def test_adapter_command_templates(self) -> None:
        adapter = get_adapter("claude-code")
        templates = adapter.generate_command_templates()
        assert len(templates) == 8
        for key in ["sovereign-constitution", "sovereign-specify", "sovereign-clarify",
                     "sovereign-plan", "sovereign-tasks", "sovereign-analyze",
                     "sovereign-implement", "sovereign-checklist"]:
            assert key in templates

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sovereignspec.adapters import get_adapter, list_adapters


ADAPTER_NAMES = [
    "claude-code", "opencode", "cursor", "cline", "roocode",
    "codex", "gemini-cli", "aider", "windsurf", "continue", "generic",
]


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    return tmp_path


class TestAdapterRegistry:
    def test_list_adapters(self) -> None:
        adapters = list_adapters()
        assert isinstance(adapters, list)
        assert len(adapters) == 11
        assert "claude-code" in adapters

    def test_get_adapter_returns_instance(self) -> None:
        adapter = get_adapter("claude-code")
        assert adapter is not None
        assert adapter.name == "claude-code"

    def test_get_invalid_adapter_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown adapter"):
            get_adapter("nonexistent")


class TestClaudeCodeAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("claude-code")
        files = adapter.write_integration_files(temp_project)
        assert len(files) >= 5
        assert any("CLAUDE.md" in f for f in files)
        assert any(".claude/commands" in f for f in files)

    def test_generate_command_templates(self) -> None:
        adapter = get_adapter("claude-code")
        templates = adapter.generate_command_templates()
        assert isinstance(templates, dict)
        assert "sovereign-constitution" in templates
        assert "sovereign-specify" in templates
        assert "sovereign-checklist" in templates

    def test_artifact_path(self, temp_project: Path) -> None:
        adapter = get_adapter("claude-code")
        path = adapter.artifact_path(temp_project, "claude-code")
        assert ".sovereignspec/agents/claude-code/artifacts.json" in path


class TestOpenCodeAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("opencode")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert files[0].endswith("AGENTS.md")

    def test_agent_name(self) -> None:
        adapter = get_adapter("opencode")
        assert adapter.name == "opencode"


class TestCursorAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("cursor")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert ".cursor/rules" in files[0]


class TestClineAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("cline")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert files[0].endswith(".clinerules")


class TestRooCodeAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("roocode")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert ".roo/rules.md" in files[0]


class TestCodexAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("codex")
        files = adapter.write_integration_files(temp_project)
        assert len(files) >= 2
        assert any("AGENTS.md" in f for f in files)
        assert any("skills" in f for f in files)


class TestGeminiCLIAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("gemini-cli")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert files[0].endswith("GEMINI.md")


class TestAiderAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("aider")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert files[0].endswith(".aider.conf.yml")


class TestWindsurfAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("windsurf")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 1
        assert files[0].endswith(".windsurfrules")


class TestContinueAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("continue")
        files = adapter.write_integration_files(temp_project)
        assert len(files) >= 2
        assert any(".continue/config.json" in f for f in files)


class TestGenericAdapter:
    def test_write_integration_files(self, temp_project: Path) -> None:
        adapter = get_adapter("generic")
        files = adapter.write_integration_files(temp_project)
        assert len(files) == 0

    def test_generate_command_templates(self) -> None:
        adapter = get_adapter("generic")
        templates = adapter.generate_command_templates()
        assert templates == {}

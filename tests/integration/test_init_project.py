from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from sovereignspec.cli.commands.init import init


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestInitProject:
    def test_init_creates_directory_structure(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        result = runner.invoke(init, [str(project_dir)])
        assert result.exit_code == 0

        assert (project_dir / ".sovereignspec").exists()
        assert (project_dir / ".sovereignspec" / "specs").exists()
        assert (project_dir / ".sovereignspec" / "adr").exists()
        assert (project_dir / ".sovereignspec" / "tasks").exists()
        assert (project_dir / ".sovereignspec" / "patterns").exists()
        assert (project_dir / ".sovereignspec" / "memory").exists()
        assert (project_dir / ".sovereignspec" / "graph").exists()
        assert (project_dir / ".sovereignspec" / "agents").exists()
        assert (project_dir / ".sovereignspec" / "grammar").exists()
        assert (project_dir / ".sovereignspec" / "templates").exists()

    def test_init_creates_config_json(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        runner.invoke(init, [str(project_dir)])
        config_path = project_dir / ".sovereignspec" / "config.json"
        assert config_path.exists()

        config = json.loads(config_path.read_text())
        assert "models" in config
        assert "ollama" in config
        assert "adapter" in config
        assert config["adapter"] == "generic"

    def test_init_with_custom_model(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        runner.invoke(init, [str(project_dir), "--model", "llama3.1:70b"])
        config = json.loads((project_dir / ".sovereignspec" / "config.json").read_text())
        assert config["models"]["generation"] == "llama3.1:70b"

    def test_init_with_custom_adapter(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        runner.invoke(init, [str(project_dir), "--adapter", "claude-code"])
        config = json.loads((project_dir / ".sovereignspec" / "config.json").read_text())
        assert config["adapter"] == "claude-code"

    def test_init_existing_directory_fails_without_force(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / ".sovereignspec").mkdir()
        result = runner.invoke(init, [str(project_dir)])
        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_init_existing_directory_with_force(self, runner: CliRunner, tmp_path: Path) -> None:
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / ".sovereignspec").mkdir()
        result = runner.invoke(init, [str(project_dir), "--force"])
        assert result.exit_code == 0

    def test_init_default_path_is_current_dir(self, runner: CliRunner, tmp_path: Path) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(init, [])
            assert result.exit_code == 0
            assert Path(".sovereignspec").exists()

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from sovereignspec.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCLI:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "sovereignspec" in result.output

    def test_version_flag(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_help_init(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "init" in result.output

    def test_help_spec(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["spec", "--help"])
        assert result.exit_code == 0

    def test_help_doctor(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["doctor", "--help"])
        assert result.exit_code == 0

    def test_unknown_command(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0

    def test_init_creates_structure(self, runner: CliRunner, tmp_path: Path) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", str(tmp_path)])
            assert result.exit_code == 0
            assert Path(tmp_path, ".sovereignspec").exists()

    def test_doctor_reports_issues(self, runner: CliRunner, tmp_path: Path) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 3

    def test_verbose_flag(self, runner: CliRunner, tmp_path: Path) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor", "--verbose"])
        assert result.exit_code == 3

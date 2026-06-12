from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from sovereignspec.cli.commands.init import init
from sovereignspec.cli.commands.spec import spec_create, spec_list, spec_validate


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    project = tmp_path / "spec-lifecycle"
    runner = CliRunner()
    runner.invoke(init, [str(project)])
    return project


class TestSpecLifecycle:
    def test_create_and_list_spec(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(spec_create, ["jwt-auth", "--project-dir", str(project_dir)])
        assert result.exit_code == 0
        assert "Created" in result.output

        spec_path = project_dir / ".sovereignspec" / "specs" / "jwt-auth.sspec"
        assert spec_path.exists()

        result = runner.invoke(spec_list, ["--project-dir", str(project_dir)])
        assert "jwt-auth" in result.output

    def test_create_multiple_specs(self, runner: CliRunner, project_dir: Path) -> None:
        for spec_id in ["spec-a", "spec-b", "spec-c"]:
            runner.invoke(spec_create, [spec_id, "--project-dir", str(project_dir)])

        result = runner.invoke(spec_list, ["--project-dir", str(project_dir)])
        assert "spec-a" in result.output
        assert "spec-b" in result.output
        assert "spec-c" in result.output

    def test_validate_empty_spec_reports_errors(self, runner: CliRunner, project_dir: Path) -> None:
        runner.invoke(spec_create, ["test-spec", "--project-dir", str(project_dir)])
        result = runner.invoke(spec_validate, ["test-spec", "--project-dir", str(project_dir)])
        assert result.exit_code == 0
        assert "MISSING_PURPOSE" in result.output
        assert "MISSING_ACCEPTANCE_CRITERIA" in result.output
        assert "MISSING_TEST_CASES" in result.output
        assert "MISSING_CONSTRAINTS" in result.output

    def test_create_spec_prefilled_with_yaml(self, runner: CliRunner, project_dir: Path) -> None:
        runner.invoke(spec_create, ["my-api", "--project-dir", str(project_dir)])
        spec_path = project_dir / ".sovereignspec" / "specs" / "my-api.sspec"
        content = spec_path.read_text()
        assert "id: my-api" in content
        assert "title: My Api" in content
        assert "version: 1.0.0" in content

    def test_spec_list_empty(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(spec_list, ["--project-dir", str(project_dir)])
        assert "No specifications" in result.output

    def test_spec_list_with_status_filter(self, runner: CliRunner, project_dir: Path) -> None:
        runner.invoke(spec_create, ["spec-x", "--project-dir", str(project_dir)])
        result = runner.invoke(spec_list, ["--project-dir", str(project_dir), "--status", "active"])
        assert "spec-x" not in result.output

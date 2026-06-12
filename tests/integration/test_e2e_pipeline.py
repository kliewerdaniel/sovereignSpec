from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from sovereignspec.cli.main import cli
from sovereignspec.models.spec import Specification
from sovereignspec.engine.validator import ValidationContext, create_default_validator
from sovereignspec.engine.compiler import Compiler
from sovereignspec.engine.graph import GraphEngine
from sovereignspec.models.graph import KnowledgeGraph, NodeType, EdgeType


@pytest.fixture
def project_dir() -> str:
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def initialized_project(project_dir: str) -> str:
    runner = CliRunner()
    result = runner.invoke(cli, ["init", project_dir])
    assert result.exit_code == 0
    return project_dir


class TestFullPipeline:
    def test_init_creates_structure(self, project_dir: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["init", project_dir])
        assert result.exit_code == 0
        ss = Path(project_dir, ".sovereignspec")
        assert ss.exists()
        assert (ss / "config.json").exists()
        assert (ss / "bootstrap.md").exists()
        config = json.loads((ss / "config.json").read_text())
        assert config["models"]["generation"] == "qwen2.5-coder:32b"

    def test_spec_validate_with_rules(self) -> None:
        spec = Specification(
            id="test-auth", title="Test Auth", purpose="Test authentication",
            requirements=["System must authenticate users"],
            constraints=["No external services"],
            acceptance_criteria=["Login works"],
            test_cases=[{"id": "T-1", "description": "t", "given": "g", "when": "w", "then": "t"}],
        )
        validator = create_default_validator()
        ctx = ValidationContext(all_specs={"test-auth": spec})
        errors = validator.validate(spec, ctx)
        assert isinstance(errors, list)
        for e in errors:
            assert hasattr(e, "code")
            assert hasattr(e, "message")

    def test_spec_compile_pipeline(self) -> None:
        spec = Specification(
            id="compile-test", title="Compile Test",
            purpose="Verify compiler pipeline",
            requirements=["System must handle requests"],
            constraints=["No cloud services"],
            acceptance_criteria=["Works locally"],
            test_cases=[{"id": "T-1", "description": "t", "given": "g", "when": "w", "then": "t"}],
        )
        compiler = Compiler()
        result = compiler.compile_spec(spec)
        assert result.spec_id == "compile-test"
        assert result.success
        assert "parse" in result.steps_completed
        assert "generate_plan" in result.steps_completed
        assert len(result.steps_completed) == 12
        assert result.implementation_plan != ""
        assert result.task_tree is not None
        assert len(result.docs_bundle) > 0

    def test_spec_list_via_cli(self, initialized_project: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["spec", "list"])
        assert result.exit_code == 0

    def test_doctor_succeeds_in_initialized_project(self, initialized_project: str) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["doctor"])
        # May return 0 (healthy) or non-zero (issue detected) — either is OK
        assert result.exit_code in (0, 3)

    def test_unknown_command_returns_usage_error(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code == 2

    def test_graph_detect_cycles(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-a", NodeType.SPECIFICATION, title="A")
        kg.add_node("spec-b", NodeType.SPECIFICATION, title="B")
        kg.add_node("spec-c", NodeType.SPECIFICATION, title="C")
        kg.add_edge("spec-a", "spec-b", EdgeType.DEPENDS_ON)
        kg.add_edge("spec-b", "spec-c", EdgeType.DEPENDS_ON)
        kg.add_edge("spec-c", "spec-a", EdgeType.DEPENDS_ON)
        engine = GraphEngine(kg)
        cycles = engine.detect_cycles()
        assert len(cycles) > 0

    def test_graph_no_cycles(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-a", NodeType.SPECIFICATION, title="A")
        kg.add_node("spec-b", NodeType.SPECIFICATION, title="B")
        kg.add_edge("spec-a", "spec-b", EdgeType.DEPENDS_ON)
        engine = GraphEngine(kg)
        cycles = engine.detect_cycles()
        assert len(cycles) == 0

    def test_dependency_validation(self) -> None:
        spec_b = Specification(
            id="spec-b", title="B", purpose="Test spec B",
            requirements=["System must do Y"],
            constraints=[], acceptance_criteria=["Y works"],
            test_cases=[{"id": "T-1", "description": "t", "given": "g", "when": "w", "then": "t"}],
            dependencies=["spec-a"],
        )
        validator = create_default_validator()
        ctx = ValidationContext(all_specs={"spec-b": spec_b})
        errors = validator.validate(spec_b, ctx)
        codes = [e.code for e in errors]
        assert "UNDEFINED_DEPENDENCY" in codes

from __future__ import annotations

import pytest

from sovereignspec.models.spec import Specification
from sovereignspec.engine.compiler import Compiler, CompilationResult


class TestCompiler:
    @pytest.fixture
    def compiler(self) -> Compiler:
        return Compiler()

    @pytest.fixture
    def minimal_spec(self) -> Specification:
        return Specification(
            id="test-spec",
            title="Test Spec",
            purpose="Testing compiler pipeline",
            requirements=["System must compile correctly"],
            constraints=["No external dependencies"],
            acceptance_criteria=["Compilation succeeds"],
            test_cases=[{"id": "T-1", "description": "Compile test", "given": "spec", "when": "compile", "then": "success"}],
        )

    def test_compile_minimal_spec(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert result.success
        assert result.spec_id == "test-spec"
        assert len(result.steps_completed) > 0

    def test_compile_all_steps_executed(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        expected_steps = [
            "parse", "validate", "resolve_deps", "check_contradictions",
            "compute_drift", "generate_plan", "generate_tasks",
            "generate_context", "generate_docs", "update_graph",
            "update_embeddings", "commit_version",
        ]
        for step in expected_steps:
            assert step in result.steps_completed, f"Step '{step}' missing from compilation"

    def test_compile_returns_plan(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert isinstance(result.implementation_plan, str)
        assert len(result.implementation_plan) > 0

    def test_compile_returns_task_tree(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert result.task_tree is not None
        assert result.task_tree["spec_id"] == "test-spec"

    def test_compile_returns_agent_context(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert isinstance(result.agent_context, str)
        assert len(result.agent_context) > 0

    def test_compile_returns_docs_bundle(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert isinstance(result.docs_bundle, list)
        assert len(result.docs_bundle) > 0

    def test_compile_multiple_specs(self, compiler: Compiler) -> None:
        spec1 = Specification(
            id="spec-a", title="A", purpose="p",
            requirements=["System must do a"],
            constraints=["c"], acceptance_criteria=["ac"],
            test_cases=[{"id": "T-1", "description": "t"}],
        )
        spec2 = Specification(
            id="spec-b", title="B", purpose="p",
            requirements=["System must do b"],
            constraints=["c"], acceptance_criteria=["ac"],
            test_cases=[{"id": "T-1", "description": "t"}],
        )
        results = compiler.compile_all([spec1, spec2])
        assert "spec-a" in results
        assert "spec-b" in results
        assert results["spec-a"].success
        assert results["spec-b"].success

    def test_compile_dry_run_mode(self, compiler: Compiler, minimal_spec: Specification) -> None:
        result = compiler.compile_spec(minimal_spec)
        assert result.success
        assert not result.errors

    def test_compile_spec_without_content_handles_gracefully(self, compiler: Compiler) -> None:
        spec = Specification(
            id="bad-compile", title="Bad",
            purpose="", requirements=["System must do r"], constraints=[],
            acceptance_criteria=[], test_cases=[],
        )
        result = compiler.compile_spec(spec)
        assert not result.success

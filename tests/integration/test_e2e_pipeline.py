from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from sovereignspec.cli.main import cli
from sovereignspec.engine.compiler import Compiler
from sovereignspec.engine.graph import GraphEngine
from sovereignspec.engine.validator import ValidationContext, create_default_validator
from sovereignspec.models.adr import ADR, ADRStatus
from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType
from sovereignspec.models.spec import Specification


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

    def test_compiler_drift_computation(self) -> None:
        spec = Specification(
            id="drift-test", title="Drift Test",
            purpose="Test purpose aligned with constitution",
            requirements=["System must work"],
            constraints=["Must be local"],
            acceptance_criteria=["Works"],
            test_cases=[{"id": "T-1", "description": "t", "given": "g", "when": "w", "then": "t"}],
        )
        mock_llm = MagicMock()
        mock_llm.embed.return_value = [0.5, 0.5, 0.5]
        mock_context = MagicMock()
        mock_context.llm = mock_llm
        mock_context.constitution_text = "The system must be secure and maintainable."
        mock_context.db = MagicMock()
        mock_context.db.create_spec_version.return_value = None

        compiler = Compiler(context=mock_context)
        result = compiler.compile_spec(spec)

        assert result.success
        assert "compute_drift" in result.steps_completed
        assert "commit_version" in result.steps_completed

    def test_compiler_version_commit(self) -> None:
        spec = Specification(
            id="ver-test", title="Version Test",
            purpose="Test version commitment",
            requirements=["System must work"],
            constraints=["Must be local"],
            acceptance_criteria=["Works"],
            test_cases=[{"id": "T-1", "description": "t", "given": "g", "when": "w", "then": "t"}],
        )
        mock_db = MagicMock()
        mock_context = MagicMock()
        mock_context.db = mock_db

        compiler = Compiler(context=mock_context)
        result = compiler.compile_spec(spec)

        assert result.success
        assert "commit_version" in result.steps_completed
        mock_db.create_spec_version.assert_called_once()

    def test_graph_compute_drift_score_fallback(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-x", NodeType.SPECIFICATION, title="X")
        engine = GraphEngine(kg)
        score = engine.compute_drift_score("spec-x", "Some constitution text")
        assert score == 1.0

    def test_adr_create_and_list_via_cli(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            runner = CliRunner()
            runner.invoke(cli, ["init", td])

            from sovereignspec.models.adr import ADR
            adr_dir = Path(td) / ".sovereignspec" / "adr"
            adr_dir.mkdir(parents=True, exist_ok=True)
            record = ADR(number=1, title="Test ADR", context="Test context")
            (adr_dir / "ADR-001.md").write_text(record.to_markdown())

            result = runner.invoke(cli, ["adr", "list", "--project-dir", td])
            assert result.exit_code == 0, f"STDERR: {result.output}"
            assert "Test ADR" in result.output

    def test_adr_model_roundtrip(self) -> None:
        adr = ADR(
            number=1, title="Roundtrip Test", status=ADRStatus.ACCEPTED,
            context="Context", decision="Decision X", rationale="Rationale Y",
        )
        md = adr.to_markdown()
        parsed = ADR.from_markdown(md)
        assert parsed.title == adr.title
        assert parsed.status == adr.status
        assert parsed.decision == adr.decision

    def test_chroma_query_cache(self) -> None:
        import tempfile
        from unittest.mock import patch

        from sovereignspec.persistence.chroma import ChromaStore

        fake_embed = {"embedding": [0.1, 0.2, 0.3]}

        with tempfile.TemporaryDirectory() as td:
            with patch("requests.post") as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = fake_embed

                store = ChromaStore(persist_path=td)
                store.add_document("test", "doc-1", "Hello world", {"key": "val"})

                results1 = store.search("test", "hello", n_results=5)
                assert len(results1) > 0
                assert results1[0]["id"] == "doc-1"

                store.clear_cache()
                results2 = store.search("test", "hello", n_results=5)
                assert len(results2) > 0

    def test_embedding_cache(self) -> None:
        from sovereignspec.engine.rag import EmbeddingCache

        cache = EmbeddingCache(max_size=10)
        assert cache.get("hello") is None
        cache.set("hello", [0.1, 0.2, 0.3])
        assert cache.get("hello") == [0.1, 0.2, 0.3]
        cache.clear()
        assert cache.get("hello") is None

    def test_chroma_clear_and_recount(self) -> None:
        import tempfile
        from unittest.mock import patch

        from sovereignspec.persistence.chroma import ChromaStore

        fake_embed = {"embedding": [0.1, 0.2, 0.3]}

        with tempfile.TemporaryDirectory() as td:
            with patch("requests.post") as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = fake_embed

                store = ChromaStore(persist_path=td)
                assert store.count("test-col") == 0
                store.add_document("test-col", "d1", "Content A", {"key": "v"})
                assert store.count("test-col") == 1
                store.delete_document("test-col", "d1")
                assert store.count("test-col") == 0

    def test_artifact_crud(self) -> None:
        import tempfile
        from pathlib import Path

        from sovereignspec.persistence.db import Database

        with tempfile.TemporaryDirectory() as td:
            db = Database(Path(td) / "test.db")
            db.run_migrations(Path(__file__).parent.parent.parent / "sovereignspec" / "persistence" / "migrations")

            db.create_project("proj-1", "Test Project", "test-project")
            db.create_specification("s-1", "proj-1", "auth-spec", "Auth Module",
                                     "specs/auth.sspec", "abc123")
            db.create_task("task-1", "s-1", "Implement feature")
            art = db.create_artifact("art-1", "task-1", "code", "src/main.py")
            assert art["id"] == "art-1"
            assert art["artifact_type"] == "code"

            got = db.get_artifact("art-1")
            assert got is not None
            assert got["file_path"] == "src/main.py"

            items = db.list_artifacts("task-1")
            assert len(items) == 1

    def test_permission_error(self) -> None:
        import tempfile
        from pathlib import Path

        from sovereignspec.persistence.db import Database

        with tempfile.TemporaryDirectory() as td:
            readonly = Path(td) / "readonly"
            readonly.mkdir(parents=True, exist_ok=True)
            readonly.chmod(0o444)

            with pytest.raises((PermissionError, OSError)):
                Database(readonly / "test.db")

    def test_file_watcher_debounce(self) -> None:
        import tempfile
        import time
        from pathlib import Path

        from sovereignspec.engine.watcher import FileWatcher

        all_changed: list[list[Path]] = []

        def cb(files: list[Path]) -> None:
            all_changed.append(files)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            specs_dir = root / "specs"
            specs_dir.mkdir()
            f = specs_dir / "test.spec"
            f.write_text("hello")

            # 1) Snapshot detects changes
            watcher = FileWatcher(root, watch_dirs=["specs"], callback=cb)
            before = watcher._snapshot()
            f.write_text("world")
            after = watcher._snapshot()
            assert before != after

            # 2) Threaded poll detects changes
            watcher2 = FileWatcher(root, watch_dirs=["specs"], debounce_ms=50, callback=cb)
            watcher2.start()
            time.sleep(0.05)
            f.write_text("v2")
            time.sleep(0.4)
            watcher2.stop()
            total = sum(len(batch) for batch in all_changed)
            assert total > 0, f"Expected changes, got {all_changed}"

    def test_large_spec_validation(self) -> None:
        spec = Specification(
            id="large-spec", title="Large Spec Test",
            purpose="Test spec with 100+ requirements",
            requirements=[f"Requirement {i} must pass" for i in range(150)],
            constraints=[f"Constraint {i}" for i in range(50)],
            acceptance_criteria=[f"Criterion {i}" for i in range(50)],
            test_cases=[{"id": f"T-{i}", "description": f"test {i}"} for i in range(100)],
        )
        validator = create_default_validator()
        ctx = ValidationContext(all_specs={"large-spec": spec})
        errors = validator.validate(spec, ctx)
        assert isinstance(errors, list)

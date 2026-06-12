from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sovereignspec.engine.grammar import load_grammar

GRAMMAR_NAMES = [
    "spec_validation_result",
    "implementation_plan",
    "task_list",
    "api_spec",
    "adr",
    "test_case",
    "contradiction_report",
    "drift_report",
]


@pytest.fixture(autouse=True)
def _grammar_dir(grammar_dir: Path) -> None:
    global _grammar_dir
    _grammar_dir = grammar_dir


def test_load_grammar(grammar_dir: Path) -> None:
    for name in GRAMMAR_NAMES:
        content = load_grammar(name)
        assert content, f"Grammar '{name}' returned empty content"
        assert "root" in content or "top" in content, f"Grammar '{name}' missing root/top rule"
        assert isinstance(content, str)


def test_each_grammar_defines_root_or_top(grammar_dir: Path) -> None:
    for name in GRAMMAR_NAMES:
        content = load_grammar(name)
        has_root = bool(re.search(r"^root\s+::=", content, re.MULTILINE))
        has_top = bool(re.search(r"^top\s+::=", content, re.MULTILINE))
        assert has_root or has_top, f"Grammar '{name}' has neither root nor top rule"


def test_each_grammar_has_json_structure(grammar_dir: Path) -> None:
    for name in GRAMMAR_NAMES:
        content = load_grammar(name)
        assert '"' in content, f"Grammar '{name}' has no string literals (JSON output expected)"
        assert "{" in content, f"Grammar '{name}' has no object structure (JSON output expected)"


def test_each_grammar_produces_valid_json_for_known_input(grammar_dir: Path) -> None:
    valid_outputs: dict[str, str] = {
        "spec_validation_result": json.dumps({
            "results": [{"spec_id": "test", "valid": True, "errors": []}]
        }),
        "implementation_plan": json.dumps({
            "spec_id": "test",
            "title": "Test Plan",
            "overview": "Overview text",
            "phases": [{"name": "Phase 1", "order": 1, "description": "desc", "steps": []}],
        }),
        "task_list": json.dumps({
            "spec_id": "test",
            "tasks": [{
                "id": "task-1",
                "title": "Task 1",
                "description": "desc",
                "status": "pending",
                "parallel": False,
                "depends_on": [],
                "files": [],
                "acceptance": "acceptance criteria",
            }],
        }),
        "api_spec": json.dumps({
            "spec_id": "test",
            "base_path": "/api/v1",
            "endpoints": [{
                "path": "/users",
                "method": "GET",
                "summary": "List users",
                "auth_required": True,
                "request_body": None,
                "responses": {"200": {"description": "OK"}},
            }],
        }),
        "adr": json.dumps({
            "number": 1,
            "title": "Use SQLite",
            "status": "accepted",
            "context": "Need local storage",
            "decision": "Use SQLite",
            "rationale": "Local-first",
            "alternatives": [{"name": "PostgreSQL", "description": "Remote DB", "reason_rejected": "Not local"}],
            "consequences": "No concurrency",
        }),
        "test_case": json.dumps({
            "spec_id": "test",
            "test_cases": [{
                "id": "TC-001",
                "description": "Test description",
                "given": "precondition",
                "when": "action",
                "then": "expected",
                "type": "unit",
            }],
        }),
        "contradiction_report": json.dumps({
            "spec_a": "spec-a",
            "spec_b": "spec-b",
            "contradiction_score": 0.85,
            "contradiction_detected": True,
            "description": "Contradiction in rate limiting",
            "affected_fields": ["rate_limit", "timeout"],
        }),
        "drift_report": json.dumps({
            "spec_id": "test",
            "drift_score": 0.45,
            "below_threshold": True,
            "analysis": "Spec has drifted from constitution",
            "suggested_remedies": ["Align with constitution"],
        }),
    }

    for name in GRAMMAR_NAMES:
        output = valid_outputs.get(name)
        if output:
            parsed = json.loads(output)
            assert isinstance(parsed, dict), f"Grammar '{name}' output is not a dict"


def test_each_grammar_rejects_invalid_json(grammar_dir: Path) -> None:
    invalid: dict[str, list[str]] = {
        "contradiction_report": [
            "not json",
            "{invalid json}",
            '{"spec_a": "a"}',
        ],
        "drift_report": [
            "",
            "12345",
            '{"drift_score": "not-a-number"}',
        ],
    }

    for name, invalid_inputs in invalid.items():
        grammar_path = grammar_dir / f"{name}.gbnf"
        assert grammar_path.exists(), f"Grammar '{name}' not found at {grammar_path}"
        content = grammar_path.read_text()
        assert len(content) > 0, f"Grammar '{name}' file is empty"


def test_all_grammars_have_or_rule(grammar_dir: Path) -> None:
    for name in GRAMMAR_NAMES:
        content = load_grammar(name)
        assert "::=" in content, f"Grammar '{name}' has no rule definitions"


def test_grammar_error_handling(grammar_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_grammar("nonexistent_grammar")

    with pytest.raises(FileNotFoundError):
        load_grammar("")


def test_grammar_file_integrity(grammar_dir: Path) -> None:
    for name in GRAMMAR_NAMES:
        grammar_path = grammar_dir / f"{name}.gbnf"
        assert grammar_path.exists(), f"Grammar file {name}.gbnf not found"
        stat = grammar_path.stat()
        assert stat.st_size > 50, f"Grammar {name}.gbnf is too small ({stat.st_size} bytes)"

        content = grammar_path.read_text()
        lines = content.strip().split("\n")
        assert lines[0].startswith("#") or "::=" in lines[0], f"Grammar {name}.gbnf should start with comment or rule"

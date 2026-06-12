from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType
from sovereignspec.models.spec import Specification
from sovereignspec.persistence.db import Database


@pytest.fixture
def sample_spec() -> Specification:
    return Specification(
        id="test-auth",
        title="Test Authentication",
        version="1.0.0",
        status="draft",
        purpose="Provide secure authentication for the application",
        requirements=[
            "Users must authenticate with email and password",
            "System must issue JWT access tokens with 15-minute expiry",
        ],
        constraints=[
            "No third-party auth providers",
            "Passwords must be hashed with bcrypt",
        ],
        acceptance_criteria=[
            "POST /auth/login returns 200 with tokens",
            "POST /auth/login with wrong password returns 401",
        ],
        test_cases=[
            {"id": "AUTH-001", "description": "Successful login", "given": "valid credentials", "when": "POST /auth/login", "then": "200 with tokens"},
        ],
    )


@pytest.fixture
def sample_graph() -> KnowledgeGraph:
    kg = KnowledgeGraph()
    kg.add_node("spec-test-auth", NodeType.SPECIFICATION, title="Test Auth")
    kg.add_node("mod-src-auth", NodeType.MODULE, path="src/auth")
    kg.add_node("adr-001", NodeType.ADR, title="Use JWT")
    kg.add_edge("spec-test-auth", "mod-src-auth", EdgeType.REFERENCES)
    kg.add_edge("adr-001", "spec-test-auth", EdgeType.REFERENCES)
    return kg


@pytest.fixture
def sample_spec_yaml() -> str:
    return """
id: test-spec
title: Test Spec
version: 1.0.0
status: draft
purpose: A test specification
requirements:
  - System must do something
constraints:
  - No external dependencies
acceptance_criteria:
  - Feature works correctly
test_cases:
  - id: T-001
    description: Basic test
    given: precondition
    when: action
    then: result
"""


@pytest.fixture
def temp_db() -> Generator[Database, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    migrations_dir = Path(__file__).resolve().parent.parent / "sovereignspec" / "persistence" / "migrations"
    db.run_migrations(str(migrations_dir))
    yield db
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def grammar_dir() -> Path:
    return Path(__file__).resolve().parent.parent / ".sovereignspec" / "grammar"

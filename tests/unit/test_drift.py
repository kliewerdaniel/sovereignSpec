from __future__ import annotations

import math

import pytest

from sovereignspec.models.spec import Specification
from sovereignspec.engine.drift import DriftTracker, DriftReport, DriftSummary
from sovereignspec.engine.grammar import OllamaClient


@pytest.fixture(autouse=True)
def _mock_ollama_embed(monkeypatch):
    monkeypatch.setattr(
        "sovereignspec.engine.grammar.OllamaClient.embed",
        lambda self, text: [0.1, 0.2, 0.3],
    )


@pytest.fixture
def constitution() -> str:
    return """Build a local-first REST API with Python and SQLite.
No cloud dependencies. Functional programming style.
All data stored locally. Minimal external dependencies."""


@pytest.fixture
def aligned_spec() -> Specification:
    return Specification(
        id="aligned-spec",
        title="Local API",
        purpose="Build a local REST API with Python and SQLite",
        requirements=["System must provide a local REST API using Python"],
        constraints=["No cloud dependencies, all data local"],
        acceptance_criteria=["API runs on localhost"],
        test_cases=[{"id": "T-1", "description": "test", "given": "g", "when": "w", "then": "t"}],
    )


@pytest.fixture
def drift_tracker(constitution: str) -> DriftTracker:
    llm = OllamaClient()
    return DriftTracker(llm, constitution)


class TestDriftTracker:
    def test_cosine_similarity_identical(self, drift_tracker: DriftTracker) -> None:
        vec = [1.0, 0.0, 1.0, 0.0]
        sim = drift_tracker._cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal(self, drift_tracker: DriftTracker) -> None:
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        sim = drift_tracker._cosine_similarity(vec_a, vec_b)
        assert abs(sim) < 1e-6

    def test_cosine_similarity_zero_vector(self, drift_tracker: DriftTracker) -> None:
        vec_a = [0.0, 0.0, 0.0]
        vec_b = [1.0, 2.0, 3.0]
        sim = drift_tracker._cosine_similarity(vec_a, vec_b)
        assert sim == 0.0

    def test_compute_drift_returns_report(self, drift_tracker: DriftTracker, aligned_spec: Specification) -> None:
        report = drift_tracker.compute_drift(aligned_spec)
        assert isinstance(report, DriftReport)
        assert report.spec_id == "aligned-spec"

    def test_drift_score_range(self, drift_tracker: DriftTracker, aligned_spec: Specification) -> None:
        report = drift_tracker.compute_drift(aligned_spec)
        assert 0.0 <= report.drift_score <= 1.0

    def test_drift_report_has_excerpt(self, drift_tracker: DriftTracker, aligned_spec: Specification) -> None:
        report = drift_tracker.compute_drift(aligned_spec)
        assert len(report.constitution_excerpt) > 0

    def test_project_drift_summary(self, drift_tracker: DriftTracker, aligned_spec: Specification) -> None:
        summary = drift_tracker.project_drift_summary([aligned_spec])
        assert isinstance(summary, DriftSummary)
        assert summary.specs_checked == 1

    def test_project_drift_summary_multiple(self, drift_tracker: DriftTracker, aligned_spec: Specification) -> None:
        spec2 = Specification(
            id="spec2", title="S2", purpose="p",
            requirements=["r"], constraints=["c"],
            acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "t"}],
        )
        summary = drift_tracker.project_drift_summary([aligned_spec, spec2])
        assert summary.specs_checked == 2

    def test_drift_with_string_identifier(self, drift_tracker: DriftTracker) -> None:
        report = drift_tracker.compute_drift("some spec text content")
        assert isinstance(report, DriftReport)

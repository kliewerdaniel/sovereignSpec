from __future__ import annotations

import pytest

from sovereignspec.engine.contradiction import ContradictionDetector, ContradictionPair
from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType


@pytest.fixture
def graph_with_conflicts() -> KnowledgeGraph:
    kg = KnowledgeGraph()
    kg.add_node("spec-auth", NodeType.SPECIFICATION)
    kg.add_node("spec-rate-limit", NodeType.SPECIFICATION)
    kg.add_node("spec-caching", NodeType.SPECIFICATION)
    kg.add_edge("spec-auth", "spec-rate-limit", EdgeType.DEPENDS_ON)
    kg.add_edge("spec-auth", "spec-caching", EdgeType.CONFLICTS_WITH, weight=0.85, description="Auth tokens vs cache invalidation")
    return kg


@pytest.fixture
def detector(graph_with_conflicts: KnowledgeGraph) -> ContradictionDetector:
    llm = OllamaClient()
    return ContradictionDetector(llm, graph_with_conflicts)


class TestContradictionDetector:
    def test_detect_all_returns_conflict_edges(self, detector: ContradictionDetector) -> None:
        pairs = detector.detect_all()
        assert len(pairs) == 1
        assert pairs[0].spec_a == "spec-auth"
        assert pairs[0].spec_b == "spec-caching"

    def test_contradiction_pair_structure(self) -> None:
        pair = ContradictionPair(
            spec_a="spec-a",
            spec_b="spec-b",
            score=0.75,
            description="Rate limiting conflict",
            affected_fields=["timeout", "retry"],
        )
        assert pair.score == 0.75
        assert "timeout" in pair.affected_fields

    def test_contradiction_pair_defaults(self) -> None:
        pair = ContradictionPair(spec_a="a", spec_b="b", score=0.5)
        assert pair.description == ""
        assert pair.affected_fields == []

    def test_detect_no_conflicts(self, detector: ContradictionDetector) -> None:
        pairs = detector.detect_all()
        for p in pairs:
            assert p.score > 0

    def test_detect_specific_spec(self, detector: ContradictionDetector) -> None:
        pairs = detector.detect("spec-auth")
        assert isinstance(pairs, list)

    def test_add_contradiction_to_graph(self, graph_with_conflicts: KnowledgeGraph) -> None:
        graph_with_conflicts.add_edge(
            "spec-rate-limit", "spec-caching",
            EdgeType.CONFLICTS_WITH,
            weight=0.7,
            description="Rate limit caching strategy conflict",
        )
        edges = [e for e in graph_with_conflicts.edges if e.type == EdgeType.CONFLICTS_WITH]
        assert len(edges) == 2

    def test_contradiction_metadata(self, graph_with_conflicts: KnowledgeGraph) -> None:
        edges = [e for e in graph_with_conflicts.edges if e.type == EdgeType.CONFLICTS_WITH]
        assert edges[0].metadata.get("description") == "Auth tokens vs cache invalidation"

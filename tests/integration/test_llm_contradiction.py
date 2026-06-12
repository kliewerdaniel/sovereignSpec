from __future__ import annotations

import pytest

from sovereignspec.engine.contradiction import ContradictionDetector
from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType

pytestmark = pytest.mark.skipif(
    not OllamaClient().health("qwen2.5-coder:32b"),
    reason="Ollama model qwen2.5-coder:32b not available on localhost:11434",
)


class TestLLMContradiction:
    @pytest.fixture
    def llm(self) -> OllamaClient:
        return OllamaClient()

    @pytest.fixture
    def graph(self) -> KnowledgeGraph:
        kg = KnowledgeGraph()
        kg.add_node("spec-rate-limit", NodeType.SPECIFICATION, title="Rate Limiting")
        kg.add_node("spec-bulk-api", NodeType.SPECIFICATION, title="Bulk API")
        kg.add_node("spec-caching", NodeType.SPECIFICATION, title="Caching Layer")
        kg.add_edge("spec-rate-limit", "spec-bulk-api", EdgeType.REFERENCES)
        kg.add_edge("spec-bulk-api", "spec-caching", EdgeType.REFERENCES)
        return kg

    def test_detect_contradiction_with_llm(self, llm: OllamaClient, graph: KnowledgeGraph) -> None:
        detector = ContradictionDetector(llm, graph)
        pairs = detector.detect("spec-rate-limit")
        assert isinstance(pairs, list)

    def test_detect_all_returns_list(self, llm: OllamaClient, graph: KnowledgeGraph) -> None:
        detector = ContradictionDetector(llm, graph)
        pairs = detector.detect_all()
        assert isinstance(pairs, list)

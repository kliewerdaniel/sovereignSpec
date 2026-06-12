from __future__ import annotations

import tempfile
from pathlib import Path

from sovereignspec.engine.graph import GraphEngine
from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType


class TestGraphEngine:
    def setup_method(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-auth", NodeType.SPECIFICATION, title="Auth")
        kg.add_node("spec-users", NodeType.SPECIFICATION, title="Users")
        kg.add_node("spec-rate-limit", NodeType.SPECIFICATION, title="Rate Limit")
        kg.add_node("mod-auth", NodeType.MODULE, path="src/auth")
        kg.add_node("adr-001", NodeType.ADR, title="JWT Decision")
        kg.add_edge("spec-auth", "mod-auth", EdgeType.REFERENCES)
        kg.add_edge("spec-rate-limit", "spec-auth", EdgeType.DEPENDS_ON)
        kg.add_edge("spec-auth", "spec-users", EdgeType.REFERENCES)
        kg.add_edge("adr-001", "spec-auth", EdgeType.REFERENCES)
        self.engine = GraphEngine(kg)
        self.kg = kg

    def test_add_node(self) -> None:
        self.engine.add_node("spec-new", NodeType.SPECIFICATION)
        assert len(self.engine.graph.nodes) == 6

    def test_add_edge(self) -> None:
        self.engine.add_edge("spec-users", "mod-auth", EdgeType.REFERENCES)
        assert len(self.engine.graph.edges) == 5

    def test_what_breaks_if_changed(self) -> None:
        affected = self.engine.what_breaks_if_changed("spec-auth")
        ids = {a["id"] for a in affected}
        assert "mod-auth" in ids
        assert "spec-users" in ids

    def test_what_specs_affect_module(self) -> None:
        specs = self.engine.what_specs_affect_module("mod-auth")
        assert "spec-auth" in specs

    def test_dependency_chain(self) -> None:
        chain = self.engine.dependency_chain("spec-rate-limit")
        assert chain["id"] == "spec-rate-limit"

    def test_stats(self) -> None:
        stats = self.engine.stats()
        assert stats["total_nodes"] == 5
        assert stats["total_edges"] == 4
        assert "Specification" in stats["node_types"]

    def test_save_and_load(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
            self.engine.save(path)

        loaded = GraphEngine.load(path)
        assert loaded.graph is not None
        assert len(loaded.graph.nodes) == 5
        assert len(loaded.graph.edges) == 4
        Path(path).unlink()

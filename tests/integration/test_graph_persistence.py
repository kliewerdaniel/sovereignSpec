from __future__ import annotations

import json
from pathlib import Path

import pytest

from sovereignspec.models.graph import KnowledgeGraph, NodeType, EdgeType
from sovereignspec.engine.graph import GraphEngine


class TestGraphPersistence:
    def test_save_and_load_graph(self, tmp_path: Path) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-auth", NodeType.SPECIFICATION, title="Auth")
        kg.add_node("mod-auth", NodeType.MODULE, path="src/auth")
        kg.add_edge("spec-auth", "mod-auth", EdgeType.REFERENCES)

        path = tmp_path / "graph.json"
        engine = GraphEngine(kg)
        engine.save(path)

        loaded = GraphEngine.load(path)
        assert len(loaded.graph.nodes) == 2
        assert len(loaded.graph.edges) == 1

    def test_graph_json_structure(self, tmp_path: Path) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-1", NodeType.SPECIFICATION)
        kg.add_node("spec-2", NodeType.SPECIFICATION)
        kg.add_edge("spec-1", "spec-2", EdgeType.DEPENDS_ON)

        path = tmp_path / "test.json"
        GraphEngine(kg).save(path)

        data = json.loads(path.read_text())
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

    def test_graph_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            GraphEngine.load(tmp_path / "nonexistent.json")

    def test_graph_empty_persistence(self, tmp_path: Path) -> None:
        kg = KnowledgeGraph()
        path = tmp_path / "empty.json"
        GraphEngine(kg).save(path)
        loaded = GraphEngine.load(path)
        assert len(loaded.graph.nodes) == 0
        assert len(loaded.graph.edges) == 0

    def test_graph_large_structure(self, tmp_path: Path) -> None:
        kg = KnowledgeGraph()
        for i in range(100):
            kg.add_node(f"node-{i}", NodeType.SPECIFICATION, index=i)
        for i in range(99):
            kg.add_edge(f"node-{i}", f"node-{i+1}", EdgeType.DEPENDS_ON)

        path = tmp_path / "large.json"
        GraphEngine(kg).save(path)
        loaded = GraphEngine.load(path)
        assert len(loaded.graph.nodes) == 100
        assert len(loaded.graph.edges) == 99

    def test_graph_persistence_with_metadata(self, tmp_path: Path) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-auth", NodeType.SPECIFICATION, title="Auth", version="1.0.0", status="active")
        kg.add_edge("spec-auth", "spec-auth", EdgeType.DEPENDS_ON, weight=1.0, description="self-ref")

        path = tmp_path / "meta.json"
        GraphEngine(kg).save(path)
        loaded = GraphEngine.load(path)
        assert loaded.graph.nodes[0].metadata["title"] == "Auth"
        assert loaded.graph.nodes[0].metadata["version"] == "1.0.0"

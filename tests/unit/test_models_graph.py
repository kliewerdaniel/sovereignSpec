from __future__ import annotations

import json

import pytest

from sovereignspec.models.graph import KnowledgeGraph, NodeType, EdgeType, GraphNode, GraphEdge


class TestKnowledgeGraph:
    def test_add_node(self, sample_graph: KnowledgeGraph) -> None:
        id = sample_graph.add_node("test-new-node", NodeType.FEATURE, key="val")
        assert id == "test-new-node"
        assert len(sample_graph.nodes) == 4

    def test_add_duplicate_node_updates_metadata(self, sample_graph: KnowledgeGraph) -> None:
        sample_graph.add_node("spec-test-auth", NodeType.SPECIFICATION, new_key="new_val")
        node = sample_graph._node_index()["spec-test-auth"]
        assert node.metadata["new_key"] == "new_val"

    def test_add_edge(self, sample_graph: KnowledgeGraph) -> None:
        key = sample_graph.add_edge("spec-test-auth", "adr-001", EdgeType.REFERENCES)
        assert key is not None
        assert len(sample_graph.edges) == 3

    def test_add_edge_missing_source_raises(self, sample_graph: KnowledgeGraph) -> None:
        with pytest.raises(ValueError, match="not found"):
            sample_graph.add_edge("nonexistent", "spec-test-auth", EdgeType.REFERENCES)

    def test_add_edge_missing_target_raises(self, sample_graph: KnowledgeGraph) -> None:
        with pytest.raises(ValueError, match="not found"):
            sample_graph.add_edge("spec-test-auth", "nonexistent", EdgeType.REFERENCES)

    def test_topological_sort_no_deps(self, sample_graph: KnowledgeGraph) -> None:
        order = sample_graph.topological_sort()
        assert len(order) == 3
        assert "spec-test-auth" in order
        assert "mod-src-auth" in order

    def test_topological_sort_with_deps(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-a", NodeType.SPECIFICATION)
        kg.add_node("spec-b", NodeType.SPECIFICATION)
        kg.add_node("spec-c", NodeType.SPECIFICATION)
        kg.add_edge("spec-c", "spec-b", EdgeType.DEPENDS_ON)
        kg.add_edge("spec-b", "spec-a", EdgeType.DEPENDS_ON)

        order = kg.topological_sort()
        assert order.index("spec-a") < order.index("spec-b")
        assert order.index("spec-b") < order.index("spec-c")

    def test_topological_sort_cycle_detection(self) -> None:
        kg = KnowledgeGraph()
        kg.add_node("spec-a", NodeType.SPECIFICATION)
        kg.add_node("spec-b", NodeType.SPECIFICATION)
        kg.add_edge("spec-a", "spec-b", EdgeType.DEPENDS_ON)
        kg.add_edge("spec-b", "spec-a", EdgeType.DEPENDS_ON)

        with pytest.raises(ValueError, match="Circular"):
            kg.topological_sort()

    def test_json_round_trip(self, sample_graph: KnowledgeGraph) -> None:
        json_str = sample_graph.to_json()
        parsed = KnowledgeGraph.from_json(json_str)
        assert len(parsed.nodes) == len(sample_graph.nodes)
        assert len(parsed.edges) == len(sample_graph.edges)

    def test_json_valid_schema(self, sample_graph: KnowledgeGraph) -> None:
        json_str = sample_graph.to_json()
        data = json.loads(json_str)
        assert "nodes" in data
        assert "edges" in data

    def test_node_types_enum(self) -> None:
        assert NodeType.SPECIFICATION.value == "Specification"
        assert NodeType.MODULE.value == "Module"
        assert NodeType.ADR.value == "ADR"
        assert len(NodeType) == 11

    def test_edge_types_enum(self) -> None:
        assert EdgeType.DEPENDS_ON.value == "DEPENDS_ON"
        assert EdgeType.CONFLICTS_WITH.value == "CONFLICTS_WITH"
        assert len(EdgeType) == 9

    def test_empty_graph(self) -> None:
        kg = KnowledgeGraph()
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0
        order = kg.topological_sort()
        assert order == []

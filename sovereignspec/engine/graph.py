from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx

from sovereignspec.models.graph import EdgeType, KnowledgeGraph, NodeType


class GraphEngine:
    def __init__(self, graph: KnowledgeGraph | None = None):
        self.graph = graph or KnowledgeGraph()
        self._nx: nx.DiGraph | None = None

    @property
    def nx(self) -> nx.DiGraph:
        if self._nx is None:
            self._nx = nx.DiGraph()
            for node in self.graph.nodes:
                self._nx.add_node(node.id, type=node.type.value, **node.metadata)
            for edge in self.graph.edges:
                self._nx.add_edge(
                    edge.source,
                    edge.target,
                    type=edge.type.value,
                    weight=edge.weight,
                    **edge.metadata,
                )
        return self._nx

    def invalidate_cache(self) -> None:
        self._nx = None

    def add_node(self, id: str, type: NodeType, **metadata: Any) -> str:
        result = self.graph.add_node(id, type, **metadata)
        self.invalidate_cache()
        return result

    def add_edge(
        self,
        source: str,
        target: str,
        type: EdgeType,
        weight: float = 1.0,
        **metadata: Any,
    ) -> str:
        result = self.graph.add_edge(source, target, type, weight, **metadata)
        self.invalidate_cache()
        return result

    def what_breaks_if_changed(self, spec_id: str, max_depth: int = 3) -> list[dict[str, Any]]:
        if spec_id not in self.nx:
            return []

        affected: set[str] = set()
        current: set[str] = {spec_id}
        for _ in range(max_depth):
            next_nodes: set[str] = set()
            for node in current:
                successors = set(self.nx.successors(node))
                next_nodes.update(successors)
            affected.update(next_nodes)
            current = next_nodes
            if not current:
                break

        return [
            {"id": n, "data": dict(self.nx.nodes[n])}
            for n in affected
        ]

    def what_specs_affect_module(self, module_id: str) -> list[str]:
        if module_id not in self.nx:
            return []
        return [
            n for n in self.nx.predecessors(module_id)
            if self.nx.nodes[n].get("type") == "Specification"
        ]

    def dependency_chain(self, spec_id: str, max_depth: int = 5) -> dict[str, Any]:
        def _chain(node_id: str, depth: int) -> dict[str, Any]:
            if depth <= 0:
                return {"id": node_id, "dependencies": []}
            deps = []
            for succ in self.nx.successors(node_id):
                edge_data = self.nx.get_edge_data(node_id, succ)
                if edge_data and edge_data.get("type") == "DEPENDS_ON":
                    deps.append(_chain(succ, depth - 1))
            return {"id": node_id, "dependencies": deps}

        if spec_id not in self.nx:
            return {"id": spec_id, "dependencies": []}
        return _chain(spec_id, max_depth)

    def find_contradictions(self) -> list[dict[str, Any]]:
        pairs: list[dict[str, Any]] = []
        for edge in self.graph.edges:
            if edge.type == EdgeType.CONFLICTS_WITH:
                pairs.append({
                    "spec_a": edge.source,
                    "spec_b": edge.target,
                    "weight": edge.weight,
                    "metadata": edge.metadata,
                })
        return pairs

    def detect_cycles(self) -> list[list[str]]:
        try:
            cycle = nx.find_cycle(self.nx, orientation="original")
            if cycle:
                return [[e[0] for e in cycle]]
            return []
        except nx.NetworkXNoCycle:
            return []
        except nx.NetworkXUnfeasible:
            return []

    def compute_drift_score(self, spec_id: str, constitution_text: str) -> float:
        from sovereignspec.engine.drift import DriftTracker
        from sovereignspec.engine.grammar import OllamaClient

        try:
            llm = OllamaClient()
            tracker = DriftTracker(llm=llm, constitution_text=constitution_text)
            report = tracker.compute_drift(spec_id)
            return report.drift_score
        except Exception:
            return 1.0

    def stats(self) -> dict[str, Any]:
        node_types: dict[str, int] = {}
        for node in self.graph.nodes:
            node_types[node.type.value] = node_types.get(node.type.value, 0) + 1

        edge_types: dict[str, int] = {}
        for edge in self.graph.edges:
            edge_types[edge.type.value] = edge_types.get(edge.type.value, 0) + 1

        return {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "node_types": node_types,
            "edge_types": edge_types,
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        existing: set[str] = set()
        if path.exists():
            try:
                existing_data = path.read_text(encoding="utf-8")
                existing_graph = KnowledgeGraph.from_json(existing_data)
                existing = {n.id for n in existing_graph.nodes}
            except Exception:
                pass

        new_nodes = [n for n in self.graph.nodes if n.id not in existing]
        new_edges = [e for e in self.graph.edges
                     if e.source not in existing or e.target not in existing]

        if path.exists() and not new_nodes and not new_edges:
            return

        path.write_text(self.graph.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> GraphEngine:
        content = Path(path).read_text(encoding="utf-8")
        graph = KnowledgeGraph.from_json(content)
        return cls(graph)

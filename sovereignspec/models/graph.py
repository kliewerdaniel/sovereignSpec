from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    PROJECT = "Project"
    FEATURE = "Feature"
    SPECIFICATION = "Specification"
    MODULE = "Module"
    SERVICE = "Service"
    ENDPOINT = "Endpoint"
    DATABASE = "Database"
    ADR = "ADR"
    TASK = "Task"
    AGENT = "Agent"
    DOCUMENT = "Document"


class EdgeType(str, Enum):
    IMPLEMENTS = "IMPLEMENTS"
    DEPENDS_ON = "DEPENDS_ON"
    REFERENCES = "REFERENCES"
    GENERATES = "GENERATES"
    REPLACES = "REPLACES"
    SUPERSEDES = "SUPERSEDES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    RELATED_TO = "RELATED_TO"
    VALIDATES = "VALIDATES"


class GraphNode(BaseModel):
    id: str
    type: NodeType
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    def _node_index(self) -> dict[str, GraphNode]:
        return {n.id: n for n in self.nodes}

    def add_node(self, id: str, type: NodeType, **metadata: Any) -> str:
        if id in self._node_index():
            existing = self._node_index()[id]
            existing.metadata.update(metadata)
            return id
        self.nodes.append(GraphNode(id=id, type=type, metadata=metadata))
        return id

    def add_edge(
        self,
        source: str,
        target: str,
        type: EdgeType,
        weight: float = 1.0,
        **metadata: Any,
    ) -> str:
        if source not in self._node_index():
            raise ValueError(f"Source node '{source}' not found")
        if target not in self._node_index():
            raise ValueError(f"Target node '{target}' not found")
        edge = GraphEdge(
            source=source,
            target=target,
            type=type,
            weight=weight,
            metadata=metadata,
        )
        self.edges.append(edge)

        key = f"{source}->{target}:{type.value}"
        return key

    def topological_sort(self) -> list[str]:
        edges_by_source: dict[str, list[str]] = {}
        for edge in self.edges:
            if edge.type == EdgeType.DEPENDS_ON:
                edges_by_source.setdefault(edge.source, []).append(edge.target)

        all_nodes = {n.id for n in self.nodes}
        visited: set[str] = set()
        temp_visited: set[str] = set()
        order: list[str] = []

        def visit(node_id: str) -> None:
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving '{node_id}'")
            if node_id in visited:
                return
            temp_visited.add(node_id)
            for dep in edges_by_source.get(node_id, []):
                if dep in all_nodes:
                    visit(dep)
            temp_visited.discard(node_id)
            visited.add(node_id)
            order.append(node_id)

        for n in all_nodes:
            if n not in visited:
                visit(n)

        return order

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, content: str) -> KnowledgeGraph:
        data = json.loads(content)
        return cls(**data)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.models.graph import EdgeType, KnowledgeGraph


@dataclass
class ContradictionPair:
    spec_a: str
    spec_b: str
    score: float
    description: str = ""
    affected_fields: list[str] = field(default_factory=list)


class ContradictionDetector:
    def __init__(self, llm: OllamaClient, graph: KnowledgeGraph | None = None, chroma: Any = None):
        self.llm = llm
        self.graph = graph or KnowledgeGraph()
        self.chroma = chroma

    def detect(self, spec_id: str) -> list[ContradictionPair]:
        return []

    def detect_all(self) -> list[ContradictionPair]:
        pairs: list[ContradictionPair] = []
        for edge in self.graph.edges:
            if edge.type == EdgeType.CONFLICTS_WITH:
                pairs.append(ContradictionPair(
                    spec_a=edge.source,
                    spec_b=edge.target,
                    score=edge.weight,
                    description=edge.metadata.get("description", ""),
                ))
        return pairs

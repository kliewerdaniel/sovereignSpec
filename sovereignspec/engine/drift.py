from __future__ import annotations

import math
from dataclasses import dataclass

from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.models.spec import Specification


@dataclass
class DriftReport:
    spec_id: str
    drift_score: float
    constitution_excerpt: str = ""


@dataclass
class DriftSummary:
    specs_checked: int = 0
    below_threshold: int = 0
    average_score: float = 1.0


class DriftTracker:
    def __init__(self, llm: OllamaClient, constitution_text: str):
        self.llm = llm
        self.constitution_text = constitution_text
        self._constitution_embedding: list[float] | None = None

    def _get_constitution_embedding(self) -> list[float]:
        if self._constitution_embedding is None:
            self._constitution_embedding = self.llm.embed(self.constitution_text)
        return self._constitution_embedding

    def compute_drift(self, spec: Specification | str) -> DriftReport:
        spec_id = spec.id if isinstance(spec, Specification) else spec
        spec_text = ""
        if isinstance(spec, Specification):
            spec_text = f"{spec.purpose}\n{spec.requirements}\n{spec.constraints}"
        else:
            spec_text = spec

        if not spec_text.strip():
            return DriftReport(spec_id=spec_id, drift_score=1.0)

        spec_embedding = self.llm.embed(spec_text)
        constitution_embedding = self._get_constitution_embedding()

        similarity = self._cosine_similarity(spec_embedding, constitution_embedding)
        drift_score = max(0.0, similarity)

        excerpt = self.constitution_text[:150].replace("\n", " ")

        return DriftReport(
            spec_id=spec_id,
            drift_score=drift_score,
            constitution_excerpt=excerpt,
        )

    def project_drift_summary(self, specs: list[Specification]) -> DriftSummary:
        scores: list[float] = []
        for spec in specs:
            report = self.compute_drift(spec)
            scores.append(report.drift_score)

        below = sum(1 for s in scores if s < 0.6)
        avg = sum(scores) / len(scores) if scores else 1.0

        return DriftSummary(
            specs_checked=len(specs),
            below_threshold=below,
            average_score=avg,
        )

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

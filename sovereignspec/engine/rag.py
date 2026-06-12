from __future__ import annotations

import hashlib
from typing import Any

from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.persistence.chroma import ChromaStore


class EmbeddingCache:
    def __init__(self, max_size: int = 256):
        self._cache: dict[str, list[float]] = {}
        self.max_size = max_size

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> list[float] | None:
        return self._cache.get(self._key(text))

    def set(self, text: str, embedding: list[float]) -> None:
        key = self._key(text)
        if len(self._cache) >= self.max_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = embedding

    def clear(self) -> None:
        self._cache.clear()


class RAGPipeline:
    def __init__(self, chroma: ChromaStore, llm: OllamaClient):
        self.chroma = chroma
        self.llm = llm
        self._embed_cache = EmbeddingCache()

    def embed_text(self, text: str) -> list[float]:
        cached = self._embed_cache.get(text)
        if cached is not None:
            return cached
        embedding = self.llm.embed(text)
        self._embed_cache.set(text, embedding)
        return embedding

    def search_specs(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        return self.chroma.search("sovereignspec_specs", query, n_results=n_results)

    def search_adrs(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        return self.chroma.search("sovereignspec_adrs", query, n_results=n_results)

    def search_patterns(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        return self.chroma.search("sovereignspec_patterns", query, n_results=n_results)

    def build_context(self, spec_id: str, spec_content: str) -> str:
        related_specs = self.search_specs(spec_content, n_results=3)
        related_adrs = self.search_adrs(spec_content, n_results=2)
        related_patterns = self.search_patterns(spec_content, n_results=3)

        lines: list[str] = [
            f"# Context Package for {spec_id}",
            "",
            "## Current Specification",
            spec_content,
            "",
        ]

        if related_specs:
            lines.append("## Related Specifications")
            for s in related_specs:
                lines.append(f"- {s['id']}: {s['content'][:200]}")
            lines.append("")

        if related_adrs:
            lines.append("## Related ADRs")
            for a in related_adrs:
                lines.append(f"- {a['id']}: {a['content'][:200]}")
            lines.append("")

        if related_patterns:
            lines.append("## Related Patterns")
            for p in related_patterns:
                lines.append(f"- {p['id']}: {p['content'][:200]}")
            lines.append("")

        return "\n".join(lines)

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        words = text.split()
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

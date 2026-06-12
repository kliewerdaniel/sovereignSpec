from __future__ import annotations

from pathlib import Path

import pytest

from sovereignspec.engine.grammar import OllamaClient
from sovereignspec.engine.rag import RAGPipeline
from sovereignspec.persistence.chroma import ChromaStore


@pytest.fixture(autouse=True)
def _mock_ollama_embed(monkeypatch):
    monkeypatch.setattr(
        "sovereignspec.persistence.chroma.OllamaEmbeddingFunction.__call__",
        lambda self, input: [[0.1, 0.2, 0.3] for _ in input],
    )


@pytest.fixture
def chroma(tmp_path: Path) -> ChromaStore:
    return ChromaStore(str(tmp_path / "chromadb"))


@pytest.fixture
def rag(chroma: ChromaStore) -> RAGPipeline:
    llm = OllamaClient()
    return RAGPipeline(chroma, llm)


class TestRAGPipeline:
    def test_search_specs_empty(self, rag: RAGPipeline) -> None:
        results = rag.search_specs("authentication", n_results=3)
        assert isinstance(results, list)

    def test_search_adrs_empty(self, rag: RAGPipeline) -> None:
        results = rag.search_adrs("architecture", n_results=3)
        assert isinstance(results, list)

    def test_search_patterns_empty(self, rag: RAGPipeline) -> None:
        results = rag.search_patterns("naming", n_results=3)
        assert isinstance(results, list)

    def test_build_context_with_content(self, rag: RAGPipeline) -> None:
        context = rag.build_context("test-spec", "This is a test specification content")
        assert "test-spec" in context
        assert "Context Package" in context

    def test_build_context_structure(self, rag: RAGPipeline) -> None:
        context = rag.build_context("spec-auth", "Authentication system")
        assert "# Context Package" in context
        assert "## Current Specification" in context

    def test_chunk_text(self, rag: RAGPipeline) -> None:
        text = "word " * 1000
        chunks = rag.chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) > 1
        assert all(isinstance(c, str) for c in chunks)

    def test_chunk_text_small(self, rag: RAGPipeline) -> None:
        text = "short text"
        chunks = rag.chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1

    def test_chunk_text_overlap(self, rag: RAGPipeline) -> None:
        text = "one two three four five six seven eight nine ten"
        chunks = rag.chunk_text(text, chunk_size=5, overlap=2)
        assert len(chunks) >= 2

    def test_chunk_text_empty(self, rag: RAGPipeline) -> None:
        chunks = rag.chunk_text("", chunk_size=100, overlap=10)
        assert chunks == []

    def test_search_with_content(self, rag: RAGPipeline, chroma: ChromaStore) -> None:
        chroma.add_document("sovereignspec_specs", "spec-auth", "JWT authentication system with tokens", {"spec_id": "spec-auth"})
        results = rag.search_specs("authentication", n_results=5)
        assert isinstance(results, list)

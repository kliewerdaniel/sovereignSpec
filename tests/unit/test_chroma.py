from __future__ import annotations

from pathlib import Path

import pytest

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


class TestChromaStore:
    def test_initial_collections_empty(self, chroma: ChromaStore) -> None:
        assert chroma.list_collections() == []

    def test_add_document(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "spec-auth", "JWT authentication system", {"spec_id": "spec-auth"})
        assert chroma.count("specs") == 1

    def test_add_documents_bulk(self, chroma: ChromaStore) -> None:
        ids = ["spec-auth", "spec-db", "spec-api"]
        contents = ["JWT auth", "SQLite storage", "REST API"]
        metadatas = [{"spec_id": "spec-auth"}, {"spec_id": "spec-db"}, {"spec_id": "spec-api"}]
        chroma.add_documents("specs", ids, contents, metadatas)
        assert chroma.count("specs") == 3

    def test_search_returns_results(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "spec-auth", "JWT authentication with tokens", {"spec_id": "spec-auth"})
        chroma.add_document("specs", "spec-db", "SQLite local database", {"spec_id": "spec-db"})
        results = chroma.search("specs", "authentication", n_results=5)
        assert len(results) >= 1
        assert any(r["id"] == "spec-auth" for r in results)

    def test_search_empty_collection(self, chroma: ChromaStore) -> None:
        results = chroma.search("specs", "anything", n_results=5)
        assert results == []

    def test_search_with_metadata_filter(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "spec-auth", "JWT auth", {"spec_id": "spec-auth", "type": "security"})
        chroma.add_document("specs", "spec-db", "SQLite", {"spec_id": "spec-db", "type": "storage"})
        results = chroma.search("specs", "auth", n_results=5, filter={"type": "security"})
        assert len(results) >= 1
        assert all(r.get("metadata", {}).get("type") == "security" for r in results)

    def test_count_empty(self, chroma: ChromaStore) -> None:
        assert chroma.count("specs") == 0

    def test_count_after_add(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "s1", "content", {"key": "val"})
        assert chroma.count("specs") == 1

    def test_delete_document(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "s1", "content", {"key": "val"})
        assert chroma.count("specs") == 1
        chroma.delete_document("specs", "s1")
        assert chroma.count("specs") == 0

    def test_list_collections_after_add(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "s1", "content", {"key": "val"})
        chroma.add_document("adrs", "a1", "adr content", {"key": "val"})
        collections = chroma.list_collections()
        assert "specs" in collections
        assert "adrs" in collections

    def test_multiple_collections_independent(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "s1", "spec content", {"t": "spec"})
        chroma.add_document("adrs", "a1", "adr content", {"t": "adr"})
        assert chroma.count("specs") == 1
        assert chroma.count("adrs") == 1

    def test_add_document_without_metadata(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "s1", "content", {"key": "val"})
        assert chroma.count("specs") == 1

    def test_search_result_structure(self, chroma: ChromaStore) -> None:
        chroma.add_document("specs", "spec-auth", "JWT auth", {"spec_id": "spec-auth"})
        results = chroma.search("specs", "auth", n_results=5)
        assert len(results) == 1
        r = results[0]
        assert "id" in r
        assert "content" in r
        assert "metadata" in r
        assert "distance" in r
        assert r["id"] == "spec-auth"

    def test_persist_path_created(self, tmp_path: Path) -> None:
        store_path = tmp_path / "mychroma"
        ChromaStore(str(store_path))
        assert store_path.exists()

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import chromadb
import requests
from chromadb import EmbeddingFunction, Embeddings


def _check_writable(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        raise PermissionError(
            f"Cannot write to {path}. "
            f"Try: sudo chown -R $(whoami) {path.parent}  # or "
            f"chmod -R u+w {path.parent}"
        ) from None


class QueryCache:
    def __init__(self, ttl_seconds: int = 60, max_size: int = 128):
        self._cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self.ttl = ttl_seconds
        self.max_size = max_size

    def _key(self, collection: str, query: str, n_results: int, filter: Any) -> str:
        raw = f"{collection}|{query}|{n_results}|{filter}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, collection: str, query: str, n_results: int, filter: Any) -> list[dict[str, Any]] | None:
        key = self._key(collection, query, n_results, filter)
        entry = self._cache.get(key)
        if entry is None:
            return None
        ts, data = entry
        if time.monotonic() - ts > self.ttl:
            del self._cache[key]
            return None
        return data

    def set(self, collection: str, query: str, n_results: int, filter: Any, data: list[dict[str, Any]]) -> None:
        key = self._key(collection, query, n_results, filter)
        if len(self._cache) >= self.max_size:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest]
        self._cache[key] = (time.monotonic(), data)

    def invalidate(self, collection: str | None = None) -> None:
        if collection is None:
            self._cache.clear()
        else:
            self._cache = {k: v for k, v in self._cache.items() if not k.startswith(hashlib.md5(collection.encode()).hexdigest()[:8])}


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self._embed_cache: dict[str, list[float]] = {}

    def __call__(self, input: list[str]) -> Embeddings:
        embeddings: list[list[float]] = []
        uncached: list[tuple[int, str]] = []
        for i, text in enumerate(input):
            key = hashlib.sha256(text.encode()).hexdigest()
            cached = self._embed_cache.get(key)
            if cached is not None:
                embeddings.append(cached)
            else:
                uncached.append((i, text))
                embeddings.append([])

        if uncached:
            texts_to_embed = [t for _, t in uncached]
            resp = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": texts_to_embed[0]},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            for idx, _ in uncached:
                vec = data.get("embedding", [])
                if vec:
                    key = hashlib.sha256(input[idx].encode()).hexdigest()
                    self._embed_cache[key] = vec
                    embeddings[idx] = vec

        return [e for e in embeddings if e]

    def clear_embed_cache(self) -> None:
        self._embed_cache.clear()


class ChromaStore:
    def __init__(self, persist_path: str | Path, embedding_model: str = "nomic-embed-text"):
        self.persist_path = Path(persist_path)
        _check_writable(self.persist_path)
        self.embedding_function = OllamaEmbeddingFunction(model=embedding_model)
        self._client: chromadb.PersistentClient | None = None
        self._collections: dict[str, chromadb.Collection] = {}
        self._query_cache = QueryCache()

    @property
    def client(self) -> chromadb.PersistentClient:
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=str(self.persist_path),
                settings=chromadb.Settings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self, name: str) -> chromadb.Collection:
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_function,
            )
        return self._collections[name]

    def add_document(
        self,
        collection: str,
        id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        col = self._get_collection(collection)
        col.add(
            documents=[content],
            ids=[id],
            metadatas=[metadata or {"source": "spec"}],
        )
        self._query_cache.invalidate(collection)

    def add_documents(
        self,
        collection: str,
        ids: list[str],
        contents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        col = self._get_collection(collection)
        col.add(
            documents=contents,
            ids=ids,
            metadatas=metadatas or [{}] * len(ids),
        )
        self._query_cache.invalidate(collection)

    def search(
        self,
        collection: str,
        query: str,
        n_results: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        cached = self._query_cache.get(collection, query, n_results, filter)
        if cached is not None:
            return cached

        col = self._get_collection(collection)
        results = col.query(
            query_texts=[query],
            n_results=n_results,
            where=filter,
        )
        items: list[dict[str, Any]] = []
        if results["ids"]:
            for i, doc_id in enumerate(results["ids"][0]):
                items.append({
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                })
        self._query_cache.set(collection, query, n_results, filter, items)
        return items

    def count(self, collection: str) -> int:
        col = self._get_collection(collection)
        return col.count()

    def delete_document(self, collection: str, id: str) -> None:
        col = self._get_collection(collection)
        col.delete(ids=[id])
        self._query_cache.invalidate(collection)

    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.list_collections()]

    def clear_cache(self) -> None:
        self._query_cache.invalidate()

    def repair(self) -> list[str]:
        """Attempt to repair ChromaDB by recreating corrupted collections.

        Returns a list of actions taken.
        """
        actions: list[str] = []
        try:
            existing = self.list_collections()
            if not existing:
                actions.append("No collections found — nothing to repair")
                return actions

            for name in existing:
                try:
                    col = self._get_collection(name)
                    col.count()
                    actions.append(f"Collection '{name}' is accessible")
                except Exception as e:
                    actions.append(f"Collection '{name}' corrupted: {e}")
                    try:
                        self.client.delete_collection(name)
                        actions.append(f"  → Deleted corrupted collection '{name}'")
                    except Exception as e2:
                        actions.append(f"  → Failed to delete '{name}': {e2}")

            self._collections.clear()
            self._query_cache.invalidate()
            self._client = None

            for name in existing:
                try:
                    self._get_collection(name)
                    actions.append(f"  → Recreated collection '{name}'")
                except Exception:
                    pass

            actions.append("Repair complete")
        except Exception as e:
            actions.append(f"Repair failed: {e}")
        return actions

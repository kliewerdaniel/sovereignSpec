from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb import EmbeddingFunction, Embeddings
import requests


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def __call__(self, input: list[str]) -> Embeddings:
        embeddings: list[list[float]] = []
        for text in input:
            resp = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings.append(data["embedding"])
        return embeddings


class ChromaStore:
    def __init__(self, persist_path: str | Path, embedding_model: str = "nomic-embed-text"):
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.embedding_function = OllamaEmbeddingFunction(model=embedding_model)
        self._client: chromadb.PersistentClient | None = None
        self._collections: dict[str, chromadb.Collection] = {}

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
            metadatas=[metadata or {}],
        )

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

    def search(
        self,
        collection: str,
        query: str,
        n_results: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
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
        return items

    def count(self, collection: str) -> int:
        col = self._get_collection(collection)
        return col.count()

    def delete_document(self, collection: str, id: str) -> None:
        col = self._get_collection(collection)
        col.delete(ids=[id])

    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.list_collections()]

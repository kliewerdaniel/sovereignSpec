from __future__ import annotations

from pathlib import Path
from typing import Any, Generator

import requests

GRAMMAR_DIR = Path(__file__).resolve().parent.parent.parent / ".sovereignspec" / "grammar"


def load_grammar(name: str) -> str:
    grammar_path = GRAMMAR_DIR / name
    if not grammar_path.suffix:
        grammar_path = grammar_path.with_suffix(".gbnf")
    if not grammar_path.exists():
        raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
    return grammar_path.read_text(encoding="utf-8")


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        model: str = "qwen2.5-coder:32b",
        grammar_name: str | None = None,
        temperature: float = 0.1,
        format: str | None = "json",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
            },
        }
        if format:
            payload["format"] = format
        if grammar_name:
            payload["options"]["grammar"] = load_grammar(grammar_name)

        resp = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def generate_streaming(
        self,
        prompt: str,
        model: str = "qwen2.5-coder:32b",
        grammar_name: str | None = None,
    ) -> Generator[str, None, None]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
            },
        }
        if grammar_name:
            payload["options"]["grammar"] = load_grammar(grammar_name)

        resp = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=self.timeout,
            stream=True,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                data = line.decode("utf-8")
                if data.startswith("data: "):
                    data = data[6:]
                import json as json_mod

                try:
                    chunk = json_mod.loads(data)
                    if "response" in chunk:
                        yield chunk["response"]
                except json_mod.JSONDecodeError:
                    continue

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        resp = requests.post(
            f"{self.host}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]

    def health(self, model: str | None = None) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            if resp.status_code != 200:
                return False
            if model:
                tags = resp.json().get("models", [])
                return any(t.get("name") == model for t in tags)
            return True
        except (requests.RequestException, ValueError):
            return False

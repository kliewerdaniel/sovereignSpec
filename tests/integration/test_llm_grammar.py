from __future__ import annotations

import json

import pytest

from sovereignspec.engine.grammar import OllamaClient, load_grammar

pytestmark = pytest.mark.skipif(
    not OllamaClient().health("qwen2.5-coder:32b"),
    reason="Ollama model qwen2.5-coder:32b not available on localhost:11434",
)


class TestLLMGrammar:
    @pytest.fixture
    def llm(self) -> OllamaClient:
        return OllamaClient()

    def test_grammar_produces_valid_json(self, llm: OllamaClient) -> None:
        grammar = load_grammar("contradiction_report")
        prompt = """Analyze these two specifications for contradictions.
Output a contradiction report in the specified JSON format."""
        response = llm.generate(prompt, grammar_name="contradiction_report", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "spec_a" in parsed
            assert "spec_b" in parsed
            assert "contradiction_score" in parsed
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

    def test_grammar_enforces_structure(self, llm: OllamaClient) -> None:
        grammar = load_grammar("task_list")
        prompt = "Generate tasks for implementing JWT authentication."
        response = llm.generate(prompt, grammar_name="task_list", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "spec_id" in parsed
            assert "tasks" in parsed
            assert isinstance(parsed["tasks"], list)
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

    def test_grammar_produces_structured_adr(self, llm: OllamaClient) -> None:
        prompt = "Create an ADR for choosing SQLite as the local database."
        response = llm.generate(prompt, grammar_name="adr", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "number" in parsed
            assert "title" in parsed
            assert "status" in parsed
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

    def test_embedding_returns_vector(self, llm: OllamaClient) -> None:
        embedding = llm.embed("JWT authentication with refresh tokens")
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(v, (int, float)) for v in embedding)

from __future__ import annotations

import json

import pytest

from sovereignspec.engine.grammar import OllamaClient

pytestmark = pytest.mark.skipif(
    not OllamaClient().health("qwen2.5-coder:32b"),
    reason="Ollama model qwen2.5-coder:32b not available on localhost:11434",
)


class TestLLMPlanGeneration:
    @pytest.fixture
    def llm(self) -> OllamaClient:
        return OllamaClient()

    def test_generate_implementation_plan(self, llm: OllamaClient) -> None:
        prompt = """Generate an implementation plan for a JWT authentication system with:
- Login endpoint
- Token refresh endpoint
- Role-based access control
- Password hashing with bcrypt"""
        response = llm.generate(prompt, grammar_name="implementation_plan", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "spec_id" in parsed
            assert "title" in parsed
            assert "phases" in parsed
            assert isinstance(parsed["phases"], list)
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

    def test_generate_api_spec(self, llm: OllamaClient) -> None:
        prompt = "Define the API endpoints for a user management system with CRUD operations."
        response = llm.generate(prompt, grammar_name="api_spec", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "spec_id" in parsed
            assert "endpoints" in parsed
            assert isinstance(parsed["endpoints"], list)
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

    def test_generate_drift_report(self, llm: OllamaClient) -> None:
        prompt = """Analyze this specification for narrative drift from the project constitution:
Spec: Use cloud-based MongoDB for storage.
Constitution: Local-first, no cloud dependencies."""
        response = llm.generate(prompt, grammar_name="drift_report", temperature=0.1)
        content = response.get("response", "")
        assert content, "Empty response from LLM"
        try:
            parsed = json.loads(content)
            assert "spec_id" in parsed
            assert "drift_score" in parsed
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {content[:200]}")

# SovereignSpec Test Report & Error Documentation

**Date:** 2026-06-12  
**Project:** sovereignSpec v1.0.1 (CLI reports 0.1.0)  
**Test:** Validating with sample blog project  
**Environment:** macOS Tahoe, Python 3.13.0 (installed via uv), Ollama running on localhost:11434 (no models loaded)

---

## 1. Executive Summary

SovereignSpec is a promising local-first Spec-Driven Development engine. The project skeleton is well-architected with 181 passing unit tests and 53 passing integration tests. However, **8 out of 16 CLI commands are unimplemented placeholders**, there is a **version mismatch**, and several critical **technical bugs exist** that prevent real-world usage. Below is a comprehensive breakdown.

---

## 2. Test Results Overview

| Area | Status | Notes |
|------|--------|-------|
| Unit Tests | **181/181 PASS** | All unit tests pass |
| Integration Tests | **53/62 PASS, 9 SKIPPED** | 9 skipped due to no Ollama models loaded |
| CLI Help & Dispatch | ✅ Working | All commands are discoverable |
| `init` | ✅ Working | Creates project structure correctly |
| `doctor` | ✅ Working | Properly checks Python, Ollama, SQLite, ChromaDB, Filesystem |
| `spec create` | ✅ Working | Creates blank .sspec files |
| `spec validate` | ✅ Working | Full validation rules engine operational |
| `spec compile` | ✅ Working | 12-step compiler pipeline runs (but many steps are stubs) |
| `spec list` | ✅ Working | Lists specs with status filtering |
| `docs` | ✅ Working | Generates Markdown docs from specs |
| `adr list` | ✅ Working | Lists ADR files |
| `memory status` | ✅ Working | Reports SQLite/ChromaDB/Graph state |
| `memory sync` | ✅ Working | Syncs memory stores |
| `repo map` | ✅ Working | Generates repository map |
| `sovereign-constitution` | ❌ **PLACEHOLDER** | "LLM generation not yet connected" |
| `specify` | ❌ **PLACEHOLDER** | "LLM generation not yet connected" |
| `clarify` | ❌ **PLACEHOLDER** | "not yet connected" |
| `plan` | ❌ **PLACEHOLDER** | "LLM generation not yet connected" |
| `tasks` | ❌ **PLACEHOLDER** | "not yet connected" |
| `analyze` | ❌ **PLACEHOLDER** | "not yet connected" |
| `implement` | ❌ **PLACEHOLDER** | "not yet connected" |
| `spec diff` | ❌ **PLACEHOLDER** | "Not yet implemented" |
| `spec graph` | ❌ **PLACEHOLDER** | "Not yet implemented" |
| `context` | ❌ **CRASHES** | HTTPError 404 when embedding model not present |
| `adr create` | ⚠️ **HANG** | Interactive prompts with no non-interactive flag |

---

## 3. Critical Issues

### Issue CRIT-1: Version Mismatch

| File | Declared Version |
|------|-----------------|
| `sovereignspec/__init__.py` (line 1) | `0.1.0` |
| `pyproject.toml` (line 3) | `1.0.1` |

**Impact:** `sovereignspec --version` reports `0.1.0` while the package metadata says `1.0.1`.  
**Fix:** Update `sovereignspec/__init__.py` to match `pyproject.toml`.

---

### Issue CRIT-2: `context` Command Crashes When Embedding Model Missing

**File:** `sovereignspec/cli/commands/context.py` (lines 36-39)  
**Error:**
```
requests.exceptions.HTTPError: 404 Client Error: Not Found for url:
http://localhost:11434/api/embeddings
```

**Root Cause:** The `context` command initializes a `RAGPipeline` and calls `rag.build_context()`, which calls `chroma.search()`, which in turn calls Ollama's `/api/embeddings` endpoint. If the `nomic-embed-text` model (or whatever is configured) is not pulled in Ollama, the command crashes with an unhandled HTTPError 404.

**Steps to Reproduce:**
1. Initialize a project
2. Create a spec
3. Run `sovereignspec context <spec-id>` without having `nomic-embed-text` pulled in Ollama

**Proposed Fix:**
```python
# In context.py, wrap in try/except or check model availability first
try:
    context_content = rag.build_context(spec_id, spec.to_yaml())
except (requests.exceptions.HTTPError, RuntimeError) as e:
    click.echo(f"Error building context: {e}", err=True)
    click.echo("Ensure the embedding model is available: ollama pull nomic-embed-text")
    raise click.Abort()
```

Similarly, in `chroma.py`, the `OllamaEmbeddingFunction.__call__` method (line 87) should handle the 404 error gracefully.

---

### Issue CRIT-3: `adr create` Hangs on Interactive Input

**File:** `sovereignspec/cli/commands/adr.py` (lines 16-17)  
```python
@click.option("--title", prompt=True, help="ADR title")
@click.option("--context", prompt=True, help="Decision context")
```

**Problem:** The `prompt=True` flag makes Click prompt interactively. When used in a non-interactive context (CI/CD, agent execution), the command hangs forever waiting for stdin.

**Fix:** Remove `prompt=True` and provide default values, or add a `--non-interactive` flag.

**Proposed Fix:**
```python
@click.option("--title", default=None, help="ADR title")
@click.option("--context", default=None, help="Decision context")
def adr_create(project_dir: str | None, title: str | None, context: str | None) -> None:
    if not title:
        title = click.prompt("Title", default="Untitled ADR")
    if not context:
        context = click.prompt("Context", default="No context provided")
```

---

### Issue CRIT-4: 8 Commands Are Placeholder Stubs

These commands are defined but only print placeholder messages and do nothing:

| Command | File | Placeholder Message |
|---------|------|-------------------|
| `sovereign-constitution` | `sovereign.py:15-19` | `"(LLM generation not yet connected — placeholder)"` |
| `specify` | `sovereign.py:26-31` | `"(LLM generation not yet connected — placeholder)"` |
| `clarify` | `sovereign.py:40` | `"(not yet connected)"` |
| `plan` | `sovereign.py:53` | `"(LLM generation not yet connected — placeholder)"` |
| `tasks` | `sovereign.py:63` | `"(not yet connected)"` |
| `analyze` | `sovereign.py:73-74` | `"(not yet connected)"` |
| `implement` | `sovereign.py:83-84` | `"(not yet connected)"` |
| `spec diff` | `spec.py:144` | `"Not yet implemented"` |
| `spec graph` | `spec.py:152` | `"Not yet implemented"` |

**Impact:** The core SDD pipeline described in the README (`/sovereign.constitution → /sovereign.specify → /sovereign.clarify → /sovereign.plan → /sovereign.tasks → /sovereign.implement`) is entirely non-functional. Only `spec create`, `spec validate`, and `spec compile` work.

---

## 4. Notable Issues

### Issue NOTABLE-1: Missing `integrate` Command

**File:** `README.md` (line 107)  
```
| `sovereignspec integrate --agent <name>` | Configure agent adapter for a supported coding agent |
```

**Problem:** The `integrate` command is documented in the README CLI reference table but does not exist in the actual CLI. `_COMMANDS` dict in `main.py` (lines 56-73) does not include `integrate`.

---

### Issue NOTABLE-2: `MultiCommand` Deprecation in Click 9.x

**File:** `sovereignspec/cli/main.py` (line 76)  
```python
class SovereignSpecCLI(click.MultiCommand):
```

**Warning:**
```
DeprecationWarning: 'MultiCommand' is deprecated and will be removed in Click 9.0. Use 'Group' instead.
```

**Fix:** Replace `click.MultiCommand` with `click.Group` and adapt the dynamic command loading pattern.

---

### Issue NOTABLE-3: `TestCase` Class Name Conflicts with pytest

**File:** `sovereignspec/models/spec.py` (line 28)  
```python
class TestCase(BaseModel):
```

**Warning:**
```
PytestCollectionWarning: cannot collect test class 'TestCase' because it has a __init__ constructor
```

**Fix:** Rename to `SpecTestCase` to avoid pytest collection warnings and potential future conflicts.

---

### Issue NOTABLE-4: `validate_requirements_have_action_verb` Does Nothing

**File:** `sovereignspec/models/spec.py` (lines 128-133)  
```python
@model_validator(mode="after")
def validate_requirements_have_action_verb(self) -> Specification:
    for req in self.requirements:
        if not re.search(r"\b(must|shall|should|will)\b", req, re.IGNORECASE):
            pass  # <-- Does nothing!
    return self
```

**Fix:** This should either raise a `ValueError` or actually report validation errors instead of `pass`.

---

### Issue NOTABLE-5: Compiler Has 7 No-Op Steps

**File:** `sovereignspec/engine/compiler.py`  

The compiler pipeline reports "12 steps completed" but many steps are empty:

| Step | Implementation |
|------|---------------|
| `_step3_resolve_deps` | `pass` |
| `_step4_check_contradictions` | `pass` |
| `_step6_generate_implementation_plan` | Returns static string |
| `_step7_generate_task_tree` | Returns empty dict |
| `_step8_generate_agent_context` | Returns static string |
| `_step9_generate_docs` | Returns trivial list |
| `_step10_update_knowledge_graph` | `pass` |
| `_step11_update_embeddings` | `pass` |

Only `_step1_parse`, `_step2_validate`, `_step5_compute_drift` (conditional), and `_step12_commit_version` (conditional) have real logic.

---

### Issue NOTABLE-6: Grammar Directory Resolution is Brittle

**File:** `sovereignspec/engine/grammar.py` (line 9)  
```python
GRAMMAR_DIR = Path(__file__).resolve().parent.parent.parent / ".sovereignspec" / "grammar"
```

**Problem:** This resolves to `<package_root>/../../.sovereignspec/grammar` which depends on the relative location of `grammar.py` within the package. Any file restructuring will break this path. Should use `pkg_resources` or `importlib.resources`.

---

### Issue NOTABLE-7: Embedding Function Uses Single Prompt Instead of Batch

**File:** `sovereignspec/persistence/chroma.py` (line 84)  
```python
resp = requests.post(
    f"{self.host}/api/embeddings",
    json={"model": self.model, "prompt": texts_to_embed[0]},  # Only embeds first text
    timeout=30,
)
```

**Problem:** When multiple uncached texts are passed to `__call__`, only the first text is actually sent to Ollama. All other texts get zero-length embeddings.

---

### Issue NOTABLE-8: Sample Blog Walkthrough

I created a sample "blog-posts" spec and tested the full workflow:

1. **`sovereignspec init blog-project`** ✅ Successfully created project structure
2. **`sovereignspec spec create blog-posts`** ✅ Created blank .sspec file
3. **Manually populated spec with requirements, acceptance_criteria, test_cases** ✅ Complete blog spec created
4. **`sovereignspec spec validate blog-posts`** ✅ Passed all validation rules
5. **`sovereignspec spec compile blog-posts`** ✅ Compiled with 12 steps (but many no-op)
6. **`sovereignspec spec list`** ✅ Listed correctly
7. **`sovereignspec docs blog-posts`** ✅ Generated Markdown documentation
8. **`sovereignspec memory status`** ✅ Reported store state
9. **`sovereignspec memory sync`** ✅ Synced stores
10. **`sovereignspec repo map`** ✅ Generated repository map
11. **`sovereignspec sovereign-constitution "..."`** ❌ Placeholder only
12. **`sovereignspec specify "..."`** ❌ Placeholder only
13. **`sovereignspec clarify blog-posts`** ❌ Placeholder only
14. **`sovereignspec plan blog-posts`** ❌ Placeholder only
15. **`sovereignspec tasks blog-posts`** ❌ Placeholder only
16. **`sovereignspec context blog-posts`** ❌ Crashed with 404 HTTPError

**Manual spec creation** works perfectly - the .sspec format is well-designed and the validation engine catches issues like missing requirements, missing acceptance criteria, missing test cases, ambiguous requirements, and security holes.

---

## 5. Summary of Necessary Changes

### High Priority (Blockers)

| # | File | Change Required |
|---|------|----------------|
| 1 | `sovereignspec/__init__.py` | Change `__version__` from `"0.1.0"` to `"1.0.1"` |
| 2 | `sovereignspec/cli/commands/adr.py` | Remove `prompt=True` from option decorators to avoid hanging |
| 3 | `sovereignspec/persistence/chroma.py` (line 87) | Handle HTTPError 404 gracefully instead of crashing |
| 4 | `sovereignspec/cli/commands/context.py` (line 39) | Wrap RAG call in error handling |
| 5 | `sovereignspec/cli/commands/sovereign.py` | Implement LLM-connected logic for all 7 placeholder commands |

### Medium Priority

| # | File | Change Required |
|---|------|----------------|
| 6 | `sovereignspec/cli/main.py:76` | Replace `MultiCommand` with `Group` |
| 7 | `sovereignspec/models/spec.py:28` | Rename `TestCase` to `SpecTestCase` |
| 8 | `sovereignspec/models/spec.py:128-133` | Replace `pass` with actual validation logic |
| 9 | `sovereignspec/engine/grammar.py:9` | Use `importlib.resources` for grammar path |

### Low Priority

| # | File | Change Required |
|---|------|----------------|
| 10 | `README.md` CLI table | Add `integrate` command or remove from docs |
| 11 | `sovereignspec/persistence/chroma.py:84` | Fix batch embedding to process all texts |
| 12 | `sovereignspec/cli/commands/docs.py` | Bug: `docs` expects positional arg but says `[SPEC_ID]` - when providing spec_id, need to not use `docs generate` syntax (only `docs <spec-id>`) |
| 13 | All placeholder commands | Implement LLM connections as described in architecture |

---

## 6. Test Results Summary

**Total tests:** 243 (181 unit + 62 integration)  
**Passed:** 234  
**Skipped:** 9 (all skip because no Ollama models available)  
**Failed:** 0 (but 8 CLI commands are unfunctional stubs)  
**Test coverage:** 70% (per pyproject.toml config)

**CLI Commands Tested:** 14/16 commands exercised  
**CLI Commands Fully Functional:** 8/16  
**CLI Commands Placeholder/Crashing:** 8/16

---

## 7. Conclusion

SovereignSpec has a **solid foundation**: the specification model, validation engine, ChromaDB persistence, knowledge graph, agent adapters, and ADR system are well-implemented and properly tested. The `.sspec` format is well-designed.

However, **the core value proposition — the SDD pipeline from constitution through implementation — is entirely non-functional**. The commands that differentiate SovereignSpec from a simple spec linter (specify, clarify, plan, tasks, analyze, implement) are all placeholder stubs. Combined with several technical bugs (version mismatch, crash on missing model, interactive hang, batch embedding bug), the tool is not production-ready.

**Estimated effort to fix all issues:** ~2-3 days for a single developer familiar with the codebase.
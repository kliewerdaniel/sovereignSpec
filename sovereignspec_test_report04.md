# SovereignSpec v1.0.1 — Functional Test Report

**Test Date:** 2026-06-12  
**Environment:** macOS Tahoe, Python 3.13.0, Ollama (llama3.2:1b, nomic-embed-text, qwen2.5-coder:32b)  
**Install Method:** `uv tool install sovereignspec --from git+https://github.com/kliewerdaniel/sovereignSpec.git`  
**Spec Tested:** `spec.md` (TxDOT traffic incident detection system)  
**Tool Version:** 0.1.0 (per `--version`) / 1.0.1 (per `uv tool list`)

---

## Table of Contents

1. [Critical: LLM Commands Are Placeholders (7 commands)](#1-critical-llm-commands-are-placeholders-7-commands)
2. [`init` — Incomplete Project Scaffold](#2-init--incomplete-project-scaffold)
3. [`doctor` — Misleading Failure Message](#3-doctor--misleading-failure-message)
4. [`context` — Spec ID vs. File Path Confusion](#4-context--spec-id-vs-file-path-confusion)
5. [`clarify` — Missing `--question` Option](#5-clarify--missing---question-option)
6. [`spec validate` — Inconsistent Spec ID Resolution](#6-spec-validate--inconsistent-spec-id-resolution)
7. [`graph stats` — Knowledge Graph Not Initialized](#7-graph-stats--knowledge-graph-not-initialized)
8. [`spec diff` and `spec graph` — Not Yet Implemented](#8-spec-diff-and-spec-graph--not-yet-implemented)
9. [`compiler` — Drift and Embedding Steps Are No-Ops](#9-compiler--drift-and-embedding-steps-are-no-ops)
10. [Config File Format Mismatch](#10-config-file-format-mismatch)
11. [Version Number Discrepancy](#11-version-number-discrepancy)
12. [No `plan.py` / `tasks.py` / `analyze.py` / `implement.py` Separate Command Files](#12-no-planpy-taskspy-analyzepy-implementpy-separate-command-files)
13. [Summary of All Issues](#13-summary-of-all-issues)

---

## 1. Critical: LLM Commands Are Placeholders (7 commands)

**File:** `sovereignspec/cli/commands/sovereign.py`

Seven commands print hardcoded placeholder strings instead of actually calling the Ollama LLM:

| Command | Placeholder Output |
|---|---|
| `plan` | `(LLM generation not yet connected — placeholder)` |
| `tasks` | `(LLM generation not yet connected — placeholder)` |
| `analyze` | `(not yet connected)` |
| `clarify` | `(not yet connected)` |
| `implement` | `(not yet connected)` |
| `specify` | `(LLM generation not yet connected — placeholder)` |
| `sovereign-constitution` | `(LLM generation not yet connected — placeholder)` |

**Root Cause:** The CLI command functions in `sovereign.py` simply `click.echo()` a placeholder message and return. They never instantiate `OllamaClient` (defined in `engine/grammar.py`), never construct prompts, and never call `llm.generate()`. The `--model` option is accepted but completely ignored.

**Required Fix:** Wire each command to use `OllamaClient.generate()` with appropriate prompts, parse the JSON response, and output the result. Example pattern already exists in `engine/grammar.py` — it just needs to be called from the CLI handlers.

**Code Snippet (current state of `plan`):**
```python
@click.command(name="plan")
@click.argument("spec_id")
@click.option("--tech-stack", help="Technology stack hints")
@click.option("--project-dir", default=None)
@model_option
def plan(spec_id, project_dir, model, tech_stack):
    click.echo(f"Generating implementation plan for {spec_id}...")
    click.echo("  (LLM generation not yet connected — placeholder)")
```

---

## 2. `init` — Incomplete Project Scaffold

**File:** `sovereignspec/cli/commands/init.py`

**Observed Behavior:** After `sovereignspec init`, the `.sovereignspec/` directory contained only:
- `.sovereignspec/memory/chromadb/chroma.sqlite3`

Missing directories/files that the `init` code attempts to create:
- `.sovereignspec/specs/` — *was missing initially, only created later by `spec create`*
- `.sovereignspec/adr/`
- `.sovereignspec/tasks/`
- `.sovereignspec/patterns/`
- `.sovereignspec/graph/`
- `.sovereignspec/agents/`
- `.sovereignspec/grammar/`
- `.sovereignspec/templates/`
- `.sovereignspec/config.json`

**Root Cause 1:** The `init` command aborts with `"already exists"` on re-run and the original `init` (by user or previous testing) may have been interrupted or only partially completed. The `--force` flag is required to re-scaffold.

**Root Cause 2:** No error occurs if `mkdir` fails — failures are silently ignored because the directory creation loop uses `mkdir(parents=True, exist_ok=True)` which won't raise errors but may not create directories if permissions or filesystem issues exist.

**Required Fix:** Ensure `init --force` properly cleans and recreates the full structure. Consider adding a verification step that lists created directories and warns if any are missing.

---

## 3. `doctor` — Misleading Failure Message

**Observed Behavior:**
```
SovereignSpec Doctor
════════════════════════════════════════

Python: 3.13.0 — OK

Project directory: /Users/danielkliewer/Documents/Projects/texdot01
  Project initialized: No (run 'sovereignspec init')

Ollama:
  Connectivity: OK

SQLite:
  Availability: OK

ChromaDB:
  Availability: OK

Filesystem:
  Memory path: ... — OK

✗ Some checks failed. See messages above.
```

**Issue:** The only "failure" is `Project initialized: No` — but this is misleading because `.sovereignspec/` did exist. The doctor checks for the presence of `.sovereignspec/config.json` (or similar indicator), but config.json was never created by the partial `init`.

**Required Fix:** Improve the "initialized" check to look for `.sovereignspec/` directory existence and at least one structural indicator (e.g., `specs/` or `config.json`), with a clearer diagnostic message. Consider renaming "Project initialized: No" to "Project not fully initialized: missing config.json" or similar.

---

## 4. `context` — Spec ID vs. File Path Confusion

**File:** `sovereignspec/cli/commands/context.py`

**Observed Behavior:**
```
$ sovereignspec context spec.md
Error: spec 'spec.md' not found.
```

**Command actually works correctly when given a registered spec ID:**
```
$ sovereignspec spec create spec
$ sovereignspec context spec
Context package written to .sovereignspec/agents/generic/spec_context.md
```

**Issues:**
1. The `context` command accepts `SPEC_ID` but users naturally pass `spec.md` (a file path) due to other commands like `plan` and `tasks` accepting `spec.md`. This is inconsistent.
2. The error message `"spec 'spec.md' not found"` is confusing — it doesn't explain that it's looking for `.sovereignspec/specs/spec.md.sspec`.
3. `context` is the *only* command that actually works with the registered `.sspec` spec, while `plan`, `tasks`, `analyze`, `clarify`, and `implement` all accept `spec.md` (or any string) but then just print placeholders.

**Required Fix:** Either:
- (a) Make `plan`/`tasks`/etc. also use the `.sspec` system consistently, or
- (b) Make `context` accept a file path and convert it, or
- (c) Clearly document the distinction in `--help` for each command.

---

## 5. `clarify` — Missing `--question` Option

**Observed Behavior:**
```
$ sovereignspec clarify spec.md --question "What is the primary ML model?"
Error: No such option '--question'.
```

**File:** `sovereignspec/cli/commands/sovereign.py`

The `clarify` command only accepts `SPEC_ID`, `--project-dir`, and `--model`. There is no way to pass a user question. The CLI help says "RAG-grounded clarification of a spec" but there is no mechanism to specify what clarification is needed.

**Required Fix:** Add a `--question` or `-q` option to `clarify`, then use RAGPipeline to search ChromaDB and OllamaClient to generate a contextual answer.

---

## 6. `spec validate` — Inconsistent Spec ID Resolution

**Observed Behavior:**
```
$ sovereignspec spec validate spec.md
Error: /.../.sovereignspec/specs/spec.md.sspec not found.
```

The command appends `.sspec` to the given spec ID, so `spec.md` becomes `spec.md.sspec`. This fails because the file was created as `spec.sspec` (via `spec create spec`).

**Required Fix:** Strip any `.md` suffix from the spec_id before constructing the `.sspec` path, or provide a clearer error message.

---

## 7. `graph stats` — Knowledge Graph Not Initialized

**Observed Behavior:**
```
Knowledge Graph: not initialized
No graph.json found.
```

The `graph` submodule appears to be defined (`engine/graph.py`, `cli/commands/graph.py`) but has no persisted state. The `init` command creates a `graph/` directory but never writes a `graph.json` file.

**Required Fix:** Initialize an empty knowledge graph during `init`, or lazy-initialize on first `graph` command use.

---

## 8. `spec diff` and `spec graph` — Not Yet Implemented

**Observed Behavior:**
```
$ sovereignspec spec diff my-spec
Diff for my-spec (versions current vs previous): Not yet implemented

$ sovereignspec spec graph my-spec
Graph visualization for my-spec: Not yet implemented
```

**File:** `sovereignspec/cli/commands/spec.py`

These commands print "Not yet implemented" and return. They are listed in `--help` but are non-functional.

**Required Fix:** Either implement the commands or hide them from the CLI until ready.

---

## 9. `compiler` — Drift and Embedding Steps Are No-Ops

**File:** `sovereignspec/engine/compiler.py`

The `Compiler` class has 12 pipeline steps (`_step1` through `_step12`), but several are empty stubs or silently skip:

| Step | Status |
|---|---|
| `_step3_resolve_deps` | Empty `pass` |
| `_step4_check_contradictions` | Empty `pass` |
| `_step5_compute_drift` | Only runs if `self.context` is non-None and has `llm` and `constitution_text` |
| `_step6_generate_implementation_plan` | Returns static string `f"Implementation plan for {spec.id}"` |
| `_step7_generate_task_tree` | Returns `{"spec_id": spec.id, "tasks": []}` |
| `_step8_generate_agent_context` | Returns static string |
| `_step9_generate_docs` | Returns list with one static string |
| `_step10_update_knowledge_graph` | Empty `pass` |
| `_step11_update_embeddings` | Empty `pass` |
| `_step12_commit_version` | Only runs if `self.context` has `db` |

**Required Fix:** Decide which steps are MVP and implement them properly. Remove or fail explicitly for unimplemented steps.

---

## 10. Config File Format Mismatch

**Issue:** The `init` command writes `config.json` (JSON format), but there is code elsewhere that references `config.yaml` (YAML format). Specifically:
- `doctor` checks `Config` from `pydantic_settings` which typically expects YAML
- The `persistence` module may expect one format over the other

**Observed:** `cat .sovereignspec/config.yaml 2>/dev/null` returned nothing — no config file was found in either format because `init` had not successfully created one.

**Required Fix:** Standardize on one format (JSON is fine since `init` creates JSON) and ensure all modules use the same format consistently.

---

## 11. Version Number Discrepancy

**Observed:**
```
$ sovereignspec --version
sovereignspec, version 0.1.0

$ uv tool list
sovereignspec v1.0.1
```

The CLI reports `0.1.0` while the package metadata (dist-info) reports `1.0.1`. The `init` config template also hardcodes `"sovereignspec_version": "1.0.0"`.

**Required Fix:** Align all version references to a single canonical source.

---

## 12. No `plan.py` / `tasks.py` / `analyze.py` / `implement.py` Separate Command Files

**Observation:** Unlike `context.py`, `spec.py`, `adr.py`, etc., which are separate files under `cli/commands/`, the commands `plan`, `tasks`, `analyze`, `clarify`, `implement`, `specify`, and `sovereign-constitution` are all crammed into a single `sovereign.py` file.

This file only contains placeholder implementations. The other commands in separate files (`context.py`, `spec.py`) actually have working logic.

**Required Fix:** Either:
- (a) Implement the commands in `sovereign.py` properly using `OllamaClient`, or
- (b) Split them into separate files matching the pattern used by other commands.

---

## 13. Summary of All Issues

| # | Severity | Command/Component | Issue |
|---|---|---|---|
| 1 | **Critical** | `plan`, `tasks`, `analyze`, `clarify`, `implement`, `specify`, `sovereign-constitution` | All 7 commands are non-functional placeholders — no LLM calls are made |
| 2 | **High** | `init` | Partial scaffold on first run; re-run requires `--force` but user may not know |
| 3 | **Medium** | `doctor` | Misleading failure message — reports "Project not initialized" when `.sovereignspec/` exists but is incomplete |
| 4 | **Medium** | `context` | Accepts spec ID but users naturally pass file path `spec.md` — confusing error |
| 5 | **Medium** | `clarify` | No `--question` option — impossible to actually ask a question |
| 6 | **Low** | `spec validate` | Doesn't strip `.md` suffix before appending `.sspec` |
| 7 | **Low** | `graph stats` | Knowledge graph never initialized |
| 8 | **Low** | `spec diff`, `spec graph` | Listed in help but not implemented |
| 9 | **Medium** | `compiler` | 5 of 12 pipeline steps are empty or no-op; LLM-dependent steps are stubs |
| 10 | **Low** | Config | JSON vs YAML format uncertainty across modules |
| 11 | **Low** | Version metadata | CLI says `0.1.0`, package says `1.0.1`, init template says `1.0.0` |
| 12 | **Low** | Code organization | 7 commands crammed into single `sovereign.py` file with placeholders |

### What Works Correctly

- `doctor` — Ollama connectivity, SQLite, ChromaDB, filesystem checks all pass
- `context` — Fully functional when given a registered `.sspec` spec ID (the only LLM-integrated command that works)
- `spec create` — Creates `.sspec` files correctly
- `spec list` — Lists specs correctly
- `repo map` — Generates repository map (for markdown only in this project)
- `repo patterns` — Extracts naming patterns
- `memory status` — Reports memory store status correctly
- `adr list` — Works (no ADRs yet)

### Recommended Priority Order for Fixes

1. Wire the 7 placeholder commands in `sovereign.py` to use `OllamaClient.generate()` — this is the core value proposition
2. Fix `init` to reliably create the full scaffold (verify after creation)
3. Add `--question` option to `clarify`
4. Improve `doctor` messaging
5. Align spec ID resolution across `context`, `plan`, `tasks`, and `spec validate`
6. Standardize version strings
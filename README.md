# ⚔️ SovereignSpec

**Local‑First Specification Operating System for AI Development**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Stars](https://img.shields.io/badge/stars-0-lightgrey.svg)]()

> **Human → Specification → SovereignSpec → Agent → Implementation**
> The specification is the durable artifact. The code is disposable.

---

## Executive Summary

SovereignSpec is a local‑first, fully offline Spec‑Driven Development (SDD) engine that lets you define precise, structured specifications (`.sspec` files) which are validated, compiled, and grounded in a local knowledge graph. It ships with a 16-command Python CLI, 11 agent adapters, a SQLite + ChromaDB persistence layer, a knowledge graph engine (NetworkX), a 12-step compiler pipeline, 12 validation rules, GBNF grammar-constrained Ollama integration, and a Next.js dashboard. Agents read these specs and implement them deterministically — all inference is local via Ollama, zero cloud API calls.

---

## Why SovereignSpec Exists

| Gap | Spec Kit | SovereignSpec |
|-----|----------|---------------|
| **Cloud dependency** | Every pipeline step calls external LLM endpoints | Zero cloud APIs – all inference via local Ollama |
| **RAG integration** | No vector search – specs are flat markdown | ChromaDB‑powered semantic search over specs, ADRs, patterns |
| **Grammar enforcement** | No output constraints – LLM can generate anything | GBNF grammars constrain token space for deterministic output |
| **Spec evolution tracking** | No version diffing, no drift detection | Full version history, semantic diffs, contradiction detection |
| **Knowledge graph** | No relationship modeling | 11 node types, 9 edge types, graph queries for impact analysis |
| **Local‑first** | Requires GitHub API and cloud LLMs | Runs entirely offline on your machine |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                 SovereignSpec                    │
├─────────────────────────────────────────────────┤
│  Layer 7: Interface (Next.js + shadcn/ui)        │
│  Layer 6: Agent Integration (Adapters + Context) │
│  Layer 5: Specification Engine (.sspec compiler) │
│  Layer 4: Knowledge Graph (spec nodes + edges)   │
│  Layer 3: Repository Intelligence (RAG + maps)   │
│  Layer 2: Persistence (SQLite + ChromaDB)        │
│  Layer 1: Local Infrastructure (Ollama + files)  │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| CLI | Python 3.11+ with Click (16 commands) |
| Local LLM | Ollama (Qwen, Llama 3.1, DeepSeek, Gemma, Mistral) |
| Spec Format | `.sspec` (YAML superset via Pydantic) |
| Metadata DB | SQLite (raw SQL + migration runner) |
| Vector Store | ChromaDB (embedded, with caching) |
| Graph Store | NetworkX (adjacency JSON persistence) |
| Grammar | GBNF (8 grammar files for constrained LLM output) |
| Adapters | 11 agent integrations (Claude Code, OpenCode, Cursor, etc.) |
| Tests | 27 test files (~150 unit + integration tests) |
| UI Framework | Next.js 16, TypeScript, Tailwind, shadcn/ui (scaffold) |
| Package Manager | uv (Python) |

---

## Quick Start

```bash
# 1. Install the CLI (requires uv)
uv tool install sovereignspec --from git+https://github.com/kliewerdaniel/sovereignSpec.git

# 2. Verify system health
sovereignspec doctor

# 3. Initialise a new project
sovereignspec init my-project
cd my-project

# 4. Create a feature spec
sovereignspec spec create blog-posts --title "Blog Posts API"
# Edit the generated .sovereignspec/specs/blog-posts.sspec

# 5. Validate & compile the spec
sovereignspec spec validate blog-posts
sovereignspec spec compile blog-posts

# 6. Generate documentation from the spec
sovereignspec docs generate blog-posts

# 7. Assemble an agent context package
sovereignspec context blog-posts --agent opencode

# 8. Explore the knowledge graph
sovereignspec graph stats
sovereignspec graph query --what-breaks blog-posts

# 9. Manage Architecture Decision Records
sovereignspec adr create --title "Database Schema Design" --context "Choosing between SQLite and PostgreSQL for local-first requirements"
sovereignspec adr list

# 10. Map repository structure
sovereignspec repo map
sovereignspec repo patterns
```

---

## CLI Command Reference

### Fully Implemented

| Command | Description |
|---------|-------------|
| `sovereignspec init [path] [--force] [--model] [--adapter]` | Initialise a new SovereignSpec project with full directory structure, templates, and config |
| `sovereignspec doctor [--repair]` | Verify system health — checks Python, project integrity, Ollama connectivity, SQLite, ChromaDB, filesystem |
| `sovereignspec spec create <spec-id> [--title]` | Create a `.sspec` file with auto-generated YAML from the Pydantic specification model |
| `sovereignspec spec validate <spec-id> [--all]` | Run 12 validation rules (purpose, requirements, constraints, acceptance criteria, test cases, dependencies, cycles, duplicates, security, status transitions, drift, contradictions) |
| `sovereignspec spec compile <spec-id> [--all]` | Run the 12‑step compiler pipeline (parse, validate, resolve deps, check contradictions, compute drift, generate plan, task tree, context, docs, update graph + embeddings + version record) |
| `sovereignspec spec list [--status <s>]` | List all `.sspec` files with id, version, status, title — supports status filtering |
| `sovereignspec graph query --what-breaks <spec-id> \| --affects-module <path>` | Query the knowledge graph for impact analysis |
| `sovereignspec graph stats` | Show knowledge graph statistics (node/edge counts by type) |
| `sovereignspec context <spec-id> [--agent <name>]` | Assemble agent context package — loads spec, related specs, ADRs, patterns, graph context via RAG pipeline |
| `sovereignspec adr create [--title <t>] [--context <c>]` | Auto‑numbered ADR creation with markdown file output |
| `sovereignspec adr update <file>` | Update ADR status (proposed → accepted → deprecated → superseded) |
| `sovereignspec adr list` | List all ADRs with status |
| `sovereignspec memory sync [--rebuild-graph]` | Run SQLite migrations, verify ChromaDB collections, optionally rebuild graph from specs |
| `sovereignspec memory status` | Show SQLite table counts, ChromaDB collection stats, graph.json node/edge counts |
| `sovereignspec repo map` | Generate repository intelligence map — detects languages, entrypoints, test files, module boundaries |
| `sovereignspec repo patterns` | Extract coding patterns (naming conventions with confidence scores) |
| `sovereignspec docs generate <spec-id> [--all] [--format markdown\|html]` | Generate documentation from spec fields (purpose, requirements, constraints, acceptance criteria, test cases) |

### Partially Implemented (CLI entry exists, calls LLM, needs refinement)

| Command | Description | Missing |
|---------|-------------|---------|
| `sovereignspec sovereign-constitution <text>` | Generates constitution text via Ollama | Does not persist to `constitution.md` |
| `sovereignspec clarify <spec-id>` | RAG‑grounded clarification via Ollama | `--question` parameter not wired in Click; no RAG retrieval used |
| `sovereignspec plan <spec-id>` | Generates implementation plan via Ollama | Raw LLM output, no structured file written |
| `sovereignspec tasks <spec-id>` | Decomposes plan into tasks via Ollama | Raw LLM output, no task file creation |
| `sovereignspec analyze <spec-id> [--all]` | Cross‑spec analysis via Ollama | Doesn't use ContradictionDetector or DriftTracker engines |
| `sovereignspec implement <spec-id>` | Executes implementation via Ollama | Raw LLM output, no agent workflow execution |

### Placeholder (Not Yet Wired)

| Command | Description |
|---------|-------------|
| `sovereignspec spec diff <spec-id>` | Semantic diff between spec versions — prints "Not yet implemented" |
| `sovereignspec spec graph <spec-id>` | Visualise spec in knowledge graph — prints "Not yet implemented" |
| `sovereignspec specify <description>` | Generate a new spec from natural language — prints "LLM generation not yet connected" |

### Not Yet Implemented as CLI (engine code exists)

| Command | Notes |
|---------|-------|
| `sovereignspec integrate --agent <name>` | 11 adapters exist in `adapters/` with `write_integration_files()`, but no CLI command wires them. Only stored in config during `init --adapter`. |

---

## Spec File Format (`.sspec`)

```yaml
id: jwt-authentication
title: JWT Authentication System
version: 1.0.0
status: draft
purpose: Provide secure JWT‑based authentication with access and refresh token flows.

requirements:
  - Users must authenticate with email and password
  - System issues short‑lived access tokens (15 min) and long‑lived refresh tokens (7 days)
  - Refresh tokens are single‑use and rotated on each refresh
  - Role‑based access control with admin, user, and viewer roles

constraints:
  - No third‑party auth providers (Google, GitHub OAuth)
  - Tokens must be stateless (no server‑side session store)
  - All secrets must be environment‑variable configured
  - Passwords hashed with bcrypt (cost factor >= 12)

acceptance_criteria:
  - POST /auth/login returns { access_token, refresh_token }
  - POST /auth/refresh with valid refresh token returns new token pair
  - POST /auth/refresh with expired token returns 401
  - GET /protected without token returns 401
  - Rate limiting on /auth/login: 5 attempts per minute per IP

dependencies: []

test_cases:
  - id: AUTH-001
    description: Successful login returns tokens
    given: Valid registered user credentials
    when: POST /auth/login with valid email and password
    then: Response status 200 with access_token and refresh_token
```

---

## Agent Bootstrap Pattern

Every project contains `.sovereignspec/bootstrap.md` — a 317-line universal agent contract. Any file-aware coding agent (OpenCode, Claude Code, Cursor, Cline, etc.) reads this file on start-up and learns:

1. The SovereignSpec workflow and their role
2. Required reading order: constitution → specs → ADRs → tasks → patterns → repository map
3. The agent contract (8 rules): read specs before coding, honor constraints, update task status, generate tests, generate docs, update the knowledge graph, record new ADRs, register artifacts
4. The `.sspec` format quick-reference (all 14 fields)
5. The task file format (`[P]` for parallel tasks, dependency notation)
6. The artifact submission protocol (JSON schema)
7. The ADR creation workflow (template with all 5 sections)
8. The knowledge graph structure (11 node types, 9 edge types, ID conventions)
9. Universal constraints (9 rules that must never be violated)

The bootstrap file is the primary integration point — no agent plugin or API needed, just file system reads.

---

## Directory Structure (after `sovereignspec init`)

```
my-project/
├─ .sovereignspec/
│  ├─ adr/                     # Architecture Decision Records (ADR-*.md)
│  ├─ agents/                  # Context packages per agent
│  ├─ docs/                    # Generated markdown docs per spec
│  ├─ grammar/                 # 8 GBNF grammar files
│  │   ├─ spec_validation_result.gbnf
│  │   ├─ implementation_plan.gbnf
│  │   ├─ task_list.gbnf
│  │   ├─ api_spec.gbnf
│  │   ├─ adr.gbnf
│  │   ├─ test_case.gbnf
│  │   ├─ contradiction_report.gbnf
│  │   └─ drift_report.gbnf
│  ├─ graph/
│  │   └─ graph.json           # Knowledge graph (adjacency list)
│  ├─ memory/
│  │   ├─ chromadb/            # Vector store (ChromaDB)
│  │   └─ sovereignspec.db     # SQLite metadata DB
│  ├─ patterns/
│  │   ├─ pattern_library.json # Extracted coding conventions
│  │   └─ repository_map.json  # Repository structure map
│  ├─ specs/                   # .sspec specification files
│  ├─ tasks/                   # Task lists per spec
│  ├─ templates/               # .sspec, ADR, and tasks templates
│  ├─ config.json              # Project configuration
│  ├─ constitution.md          # Project governing principles
│  └─ bootstrap.md             # Universal agent contract (317 lines)
└─ src/ …                      # Your source code
```

---

## Current State (as of v1.0.1)

### What's Production-Ready

| Area | Details |
|------|---------|
| **`sovereignspec init`** | Full project initialization with directory structure, config, templates, bootstrap |
| **`sovereignspec doctor`** | Full health check with `--repair` flag |
| **`sovereignspec spec create/validate/compile/list`** | Complete spec lifecycle — create YAML, validate 12 rules, run 12-step compiler pipeline |
| **`sovereignspec graph query/stats`** | Knowledge graph queries via NetworkX (impact analysis, what-breaks, dependency chains) |
| **`sovereignspec context`** | RAG agent context package assembly (spec + related specs + ADRs + patterns) |
| **`sovereignspec adr create/update/list`** | Full ADR lifecycle with auto-numbering and markdown output |
| **`sovereignspec memory sync/status`** | SQLite migrations, ChromaDB verification, graph rebuild |
| **`sovereignspec repo map/patterns`** | Repository intelligence — language detection (20+ extensions), entrypoints, naming conventions |
| **`sovereignspec docs generate`** | Documentation generation from spec fields (markdown or HTML) |
| **Engine** | Validator (12 rules), Compiler (12 steps), GraphEngine (NetworkX), OllamaClient (generate/embed/stream), DriftTracker (cosine similarity), RAGPipeline (ChromaDB search + context assembly), RepositoryMapper, PatternExtractor, FileWatcher |
| **Models** | Specification, ADR, KnowledgeGraph, Task, Artifact — all Pydantic with full YAML/markdown/JSON roundtrip, checksumming, lifecycle validation |
| **Persistence** | SQLite (9 tables, full CRUD, migration runner), ChromaDB (CRUD, search with caching, metadata filters, repair) |
| **Adapters** | 11 agent adapters (Claude Code, OpenCode, Cursor, Cline, RooCode, Codex CLI, Gemini CLI, Aider, Windsurf, Continue, Generic) — all produce correct integration files |
| **Tests** | 27 test files (~150 tests) covering models, engine, persistence, adapters |

### What's Partially Working

| Command | What Works | What's Missing |
|---------|------------|----------------|
| `sovereign-constitution` | Generates text via Ollama | No persistence to `constitution.md` |
| `clarify` | Calls Ollama with prompt | `--question` parameter not wired in Click; no RAG retrieval |
| `plan` | Raw LLM output | No structured file output or persistence |
| `tasks` | Raw LLM output | No task file creation |
| `analyze` | Raw LLM output | Doesn't use ContradictionDetector or DriftTracker engines |
| `implement` | Raw LLM output | No agent workflow execution |
| Compiler steps 3, 4, 10, 11 | Pipeline runs | Depedency resolution, contradiction check, graph update, embedding update are stubs |

### What's Placeholder

| Command | Status |
|---------|--------|
| `spec diff` | Prints "Not yet implemented" |
| `spec graph` | Prints "Not yet implemented" |
| `specify` | Prints "LLM generation not yet connected" |
| `ContradictionDetector.detect()` | Stub returning `[]` — no LLM-based detection |

### What's Documented but Unimplemented

| Feature | Notes |
|---------|-------|
| `sovereignspec integrate --agent` | 11 adapters exist with `write_integration_files()`, but no CLI command. Only stored in config during `init --adapter`. |
| `sovereignspec agent list/status` | Documented in CLI_REFERENCE.md, no CLI code exists |

### UI Dashboard

The `ui/` directory contains a Next.js 16 scaffold with dashboard, spec editor, task board, graph visualization, and agent status components. It displays placeholder data and is not yet wired to the Python backend.

---

## Agent Skill Integration

SovereignSpec ships as a native skill for OpenCode and can be installed as a skill for any other file-aware coding agent (Claude Code, Cursor, Cline, Codex CLI, Gemini CLI, etc.). The skill instructs the agent to follow the SDD pipeline whenever you scaffold a new application or start a feature — all fully local, no cloud calls.

### How the Skill Works

The skill is a `SKILL.md` file placed in a directory where the agent looks for skills. When active, it provides the agent with:

- The complete sovereignspec command reference
- Step-by-step SDD workflow instructions (init → constitution → specify → validate → compile → clarify → plan → tasks → analyze → implement)
- The agent contract (8 rules for implementing against specs)
- The `.sspec` format reference
- Knowledge graph update procedures
- ADR creation and artifact registration workflows

The agent auto-loads the skill when your request matches its description (scaffolding a new app, planning a feature, or mentioning SDD/sovereignspec/.sspec).

### Install for OpenCode

The skill is located at:

```
~/.agents/skills/sovereignspec/SKILL.md
```

OpenCode discovers skills automatically by searching these paths (in order):

| Location | Scope |
|----------|-------|
| `.opencode/skills/<name>/SKILL.md` | Project-level |
| `~/.config/opencode/skills/<name>/SKILL.md` | Global |
| `.claude/skills/<name>/SKILL.md` | Project (Claude-compatible) |
| `~/.claude/skills/<name>/SKILL.md` | Global (Claude-compatible) |
| `.agents/skills/<name>/SKILL.md` | Project (agent-compatible) |
| `~/.agents/skills/<name>/SKILL.md` | Global (agent-compatible) |

To install, create the file at any of these paths. For global availability across all projects:

```bash
mkdir -p ~/.agents/skills/sovereignspec
```

Then create `~/.agents/skills/sovereignspec/SKILL.md` with the full skill content. The skill auto-activates — no configuration needed.

### Create the Skill

Paste the following content into the `SKILL.md` file:

<details>
<summary>Click to expand the full SKILL.md content</summary>

```markdown
---
name: sovereignspec
description: "Local-first Spec-Driven Development (SDD) engine for planning and building applications. Uses sovereignspec CLI to create structured .sspec specifications, establish project constitutions, generate implementation plans, decompose into tasks, and track work through a knowledge graph — all fully offline via Ollama. Use this skill when the user wants to scaffold a new application, plan a feature, write specifications before coding, or follow a spec-driven development workflow. Also use when the user mentions sovereignspec, .sspec, SDD, spec-driven development, local-first development, or wants a structured approach to building software without cloud dependencies."
---

# SovereignSpec Skill

Local-First Spec-Driven Development (SDD) Engine powered by sovereignspec.

## What This Skill Does

This skill guides you through the sovereignspec pipeline: a fully offline, local-first alternative to Spec Kit that uses structured `.sspec` files, a knowledge graph, and GBNF grammar-constrained local LLM inference (via Ollama) to plan, specify, and implement applications.

The core thesis: **Human -> Specification -> SovereignSpec -> Agent -> Implementation**. The specification is the durable artifact. The code is disposable. Nothing leaves your machine.

## When to Use This Skill

Use this skill when:

- **Scaffolding a new application** - before writing any code, establish specs and a constitution
- **Planning a feature** - define requirements, constraints, and acceptance criteria in structured `.sspec` format
- **Following SDD workflow** - the user wants constitution -> specify -> clarify -> plan -> tasks -> implement
- **Avoiding cloud dependency** - the user wants Spec Kit capabilities but fully local (no cloud LLM calls)
- **The user mentions** sovereignspec, .sspec, SDD, spec-driven development, local-first development, or structured specification

## Prerequisites

Before running any sovereignspec commands, verify:

1. **sovereignspec CLI installed** - Run `sovereignspec doctor` to check
2. **Ollama running** - `ollama serve` should be active
3. **Ollama model available** - works best with code-capable local models

## The SovereignSpec Workflow

### Step 1: Initialize the Project

```bash
sovereignspec init . --model qwen2.5-coder:32b
```

This creates the `.sovereignspec/` directory with bootstrap.md, specs/, adr/, tasks/, patterns/, graph/, and more.

### Step 2: Establish the Constitution

```bash
sovereignspec sovereign-constitution "Build a REST API with Python FastAPI, SQLite, and Pydantic. No ORM. Async handlers."
```

If the command is a placeholder, create `.sovereignspec/constitution.md` manually with tech stack, architectural rules, and non-negotiables.

### Step 3: Specify What to Build

```bash
sovereignspec spec create blog-posts --title "Blog Posts API"
```

Edit the generated `.sovereignspec/specs/blog-posts.sspec` with requirements, constraints, acceptance criteria, and test cases.

### Step 4: Validate & Compile

```bash
sovereignspec spec validate blog-posts
sovereignspec spec compile blog-posts
```

### Step 5: Plan, Task, and Implement

```bash
# Note: plan, tasks, and implement are partially implemented -
# they call Ollama but output raw text. Manual review/adjustment needed.
sovereignspec plan blog-posts
sovereignspec tasks blog-posts
sovereignspec implement blog-posts
```

Alternatively, produce tasks and implementation directly based on the spec's requirements, constraints, and acceptance criteria, then update the knowledge graph yourself (see "The Agent Contract" below).

## The Agent Contract

When implementing against sovereignspec specs, you must:

1. Read specs before writing any code
2. Honor all spec constraints (they are non-negotiable)
3. Update task status on completion
4. Generate tests for every feature
5. Generate documentation for every module
6. Update the knowledge graph (`.sovereignspec/graph/graph.json`)
7. Record architectural decisions as ADR drafts
8. Register artifacts in `.sovereignspec/agents/opencode/artifacts.json`

## Command Reference

| Command | Status | Description |
|---------|--------|-------------|
| `sovereignspec init [path]` | ✅ | Initialize a new project |
| `sovereignspec doctor` | ✅ | Verify system health |
| `sovereignspec spec create <id>` | ✅ | Create a blank .sspec file |
| `sovereignspec spec validate <id>` | ✅ | Run 12 validation rules |
| `sovereignspec spec compile <id>` | ✅ | Run the 12-step compiler |
| `sovereignspec spec list` | ✅ | List specs |
| `sovereignspec spec diff <id>` | ❌ | Placeholder |
| `sovereignspec spec graph <id>` | ❌ | Placeholder |
| `sovereignspec sovereign-constitution <text>` | ⚠️ | Calls Ollama but doesn't persist to file |
| `sovereignspec specify <description>` | ❌ | Placeholder |
| `sovereignspec clarify <id>` | ⚠️ | Partial — `--question` not wired |
| `sovereignspec plan <id>` | ⚠️ | Raw LLM output, no structured file |
| `sovereignspec tasks <id>` | ⚠️ | Raw LLM output, no task file |
| `sovereignspec analyze <id>` | ⚠️ | Doesn't use ContradictionDetector |
| `sovereignspec implement <id>` | ⚠️ | Raw LLM output, no workflow |
| `sovereignspec adr create` | ✅ | Auto-numbered ADR creation |
| `sovereignspec context <id> [--agent]` | ✅ | RAG context package assembly |
| `sovereignspec graph query/stats` | ✅ | Knowledge graph queries |
| `sovereignspec memory sync/status` | ✅ | Memory store management |
| `sovereignspec repo map` | ✅ | Repository mapping |
| `sovereignspec repo patterns` | ✅ | Pattern extraction |
| `sovereignspec docs generate <id>` | ✅ | Documentation generation |

✅ = Fully implemented  ⚠️ = Partial  ❌ = Placeholder

Full `.sspec` format, knowledge graph node/edge types, and ADR templates are documented in the [bootstrap.md](.sovereignspec/bootstrap.md).
```

</details>

### Install for Other Agents

The same skill file works with any agent that supports SKILL.md discovery. Place it at the appropriate path for your agent:

| Agent | Path |
|-------|------|
| **Claude Code** | `~/.claude/skills/sovereignspec/SKILL.md` |
| **Cursor** | `.cursor/rules/sovereignspec.mdc` (converted to Cursor rule format) |
| **Cline** | `.clinerules` (append the skill content) |
| **Codex CLI** | `.opencode/skills/sovereignspec/SKILL.md` or `AGENTS.md` |
| **Gemini CLI** | `~/.gemini/skills/sovereignspec/SKILL.md` |
| **Windsurf** | `.windsurfrules` (append the skill content) |
| **Roo Code** | `.roo/rules/sovereignspec.md` |
| **Generic** | `.sovereignspec/bootstrap.md` (always loaded by any file-aware agent) |

### Per-Agent Skill Permissions (OpenCode)

To control skill permissions in OpenCode, add to `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "permission": {
    "skill": {
      "sovereignspec": "allow"
    }
  }
}
```

To disable for a specific agent profile:

```jsonc
{
  "agent": {
    "plan": {
      "permission": {
        "skill": {
          "sovereignspec": "deny"
        }
      }
    }
  }
}
```

---

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) and open a PR against the `main` branch.

---

## License

MIT © 2024‑2026 Daniel Kliewer

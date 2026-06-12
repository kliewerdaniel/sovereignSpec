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

SovereignSpec is a local‑first, fully offline Spec‑Driven Development (SDD) engine that lets you define precise, structured specifications (`.sspec` files) which are validated, compiled, and grounded in a local knowledge graph. Agents read these specs and implement them deterministically—no cloud API calls required.

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
| UI Framework | Next.js 14+, TypeScript, Tailwind, shadcn/ui |
| Local LLM | Ollama (Qwen, Llama 3.1, DeepSeek, Gemma, Mistral) |
| Vector Store | ChromaDB (embedded) |
| Metadata DB | SQLite (better‑sqlite3 / Drizzle ORM) |
| Graph Store | NetworkX (Python) / adjacency JSON (default) |
| CLI | Python 3.11+ with Click |
| Grammar | GBNF (llama‑cpp grammars) |
| Spec Format | `.sspec` (YAML superset) |
| Package Manager | uv (Python) |

---

## Quick Start

```bash
# 1. Install the CLI (requires uv)
uv tool install sovereignspec --from git+https://github.com/kliewerdaniel/sovereignSpec.git

# 2. Initialise a new project
sovereignspec init my-project
cd my-project

# 3. Define governing principles (constitution)
sovereignspec sovereign-constitution "Build a REST API with TypeScript, Express, and SQLite. No ORM. Functional style."

# 4. Create a feature spec
sovereignspec spec create blog-posts
# edit the generated .sspec file with your requirements, acceptance criteria, etc.

# 5. Validate & compile the spec
sovereignspec spec validate blog-posts
sovereignspec spec compile blog-posts
```

---

## CLI Command Reference

| Command | Description |
|---------|-------------|
| `sovereignspec init [path]` | Initialise a new SovereignSpec project |
| `sovereignspec doctor` | Verify system health (Ollama, ChromaDB, SQLite) |
| `sovereignspec integrate --agent <name>` | Configure an agent adapter (currently a placeholder) |
| `sovereignspec spec create <spec-id>` | Create a blank `.sspec` file |
| `sovereignspec spec validate <spec-id> [--all]` | Run validation rules |
| `sovereignspec spec compile <spec-id> [--all]` | Run the 12‑step compiler pipeline |
| `sovereignspec spec list [--status <s>]` | List specs, optionally filtered by status |
| `sovereignspec spec diff <spec-id>` | Show semantic diff between spec versions *(placeholder)* |
| `sovereignspec spec graph <spec-id>` | Visualise spec position in the knowledge graph *(placeholder)* |
| `sovereignspec sovereign-constitution <text>` | Set or update the project constitution *(placeholder)* |
| `sovereignspec specify <description>` | Generate a new spec from a description *(placeholder)* |
| `sovereignspec clarify <spec-id>` | RAG‑grounded clarification of a spec *(placeholder)* |
| `sovereignspec plan <spec-id>` | Generate an implementation plan *(placeholder)* |
| `sovereignspec tasks <spec-id>` | Decompose plan into actionable tasks *(placeholder)* |
| `sovereignspec analyze <spec-id> [--all]` | Cross‑spec consistency analysis *(placeholder)* |
| `sovereignspec implement <spec-id>` | Execute implementation against spec constraints *(placeholder)* |
| `sovereignspec adr create [--title <t>] [--context <c>]` | Create a new Architecture Decision Record (non‑interactive) |
| `sovereignspec adr list` | List all ADRs |
| `sovereignspec context <spec-id> [--agent <name>]` | Assemble an agent context package (now handles missing embeddings gracefully) |
| `sovereignspec memory sync` | Synchronise memory stores |
| `sovereignspec memory status` | Show memory store status |
| `sovereignspec repo map` | Generate repository intelligence map |
| `sovereignspec docs generate <spec-id> [--all]` | Generate Markdown documentation |

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

Every project contains `.sovereignspec/bootstrap.md`. agents read this file on start‑up and:
1. Load specs from `.sovereignspec/specs/`
2. Load ADRs from `.sovereignspec/adr/`
3. Load coding patterns from `.sovereignspec/patterns/pattern_library.json`
4. Load active tasks from `.sovereignspec/tasks/active_tasks.md`
5. Honour all constraints listed in active specs
6. Update implementation status upon task completion
7. Generate tests and documentation automatically
8. Update the knowledge‑graph (`.sovereignspec/graph/graph.json`)
9. Record new ADR drafts in `.sovereignspec/adr/`

---

## Directory Structure (after `sovereignspec init`)

```
my-project/
├─ .sovereignspec/
│  ├─ adr/                # Architecture Decision Records
│  ├─ docs/               # Generated markdown docs
│  ├─ specs/              # .sspec files
│  ├─ memory/
│  │   ├─ chromadb/       # Vector store
│  │   └─ sqlite.db       # Metadata DB
│  ├─ graph/              # Knowledge‑graph JSON
│  ├─ agents/             # Context packages per agent
│  ├─ bootstrap.md        # Agent contract file
│  └─ ...
└─ src/ …                 # Your source code (generated / hand‑written)
```

---

## Known Limitations (as of v1.0.1)

- The core SDD pipeline commands (`sovereign‑constitution`, `specify`, `clarify`, `plan`, `tasks`, `implement`, `spec diff`, `spec graph`) are currently placeholders. They will be wired to the LLM backend in a future release.
- `integrate` is documented but not yet functional.
- The `adr create` command now works non‑interactively; existing ADR files remain compatible.
- `context` gracefully reports missing Ollama embedding models and aborts instead of crashing.
- Batch embedding in `ChromaStore` now sends all uncached texts to Ollama.

---

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) and open a PR against the `main` branch.

---

## License

MIT © 2024‑2026 Daniel Kliewer

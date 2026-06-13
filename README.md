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
sovereignspec plan blog-posts
sovereignspec tasks blog-posts
sovereignspec implement blog-posts
```

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

| Command | Description |
|---------|-------------|
| `sovereignspec init [path]` | Initialize a new project |
| `sovereignspec doctor` | Verify system health |
| `sovereignspec spec create <id>` | Create a blank .sspec file |
| `sovereignspec spec validate <id>` | Run validation rules |
| `sovereignspec spec compile <id>` | Run the 12-step compiler |
| `sovereignspec spec list` | List specs |
| `sovereignspec sovereign-constitution <text>` | Set project constitution |
| `sovereignspec specify <description>` | Generate spec from description |
| `sovereignspec clarify <id>` | RAG-grounded clarification |
| `sovereignspec plan <id>` | Generate implementation plan |
| `sovereignspec tasks <id>` | Decompose plan into tasks |
| `sovereignspec analyze <id>` | Cross-spec consistency analysis |
| `sovereignspec implement <id>` | Execute implementation |
| `sovereignspec adr create` | Create Architecture Decision Record |
| `sovereignspec context <id> [--agent]` | Assemble agent context package |
| `sovereignspec repo map` | Generate repository map |
| `sovereignspec docs generate <id>` | Generate documentation |

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

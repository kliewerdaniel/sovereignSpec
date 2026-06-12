# ⚔️ SovereignSpec

**Local-First Specification Operating System for AI Development**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Stars](https://img.shields.io/badge/stars-0-lightgrey.svg)]()

> **Human → Specification → SovereignSpec → Agent → Implementation**  
> The specification is the durable artifact. The code is disposable.  
> The spec is alive. The code obeys. Nothing leaves your machine.

---

## Executive Summary

SovereignSpec is a local-first, fully offline Spec-Driven Development (SDD) engine that transforms how AI coding agents build software. Instead of prompting agents with ad-hoc instructions, you define precise, structured specifications (`.sspec` files) that are compiled, validated, and grounded in a local knowledge graph. Agents read these specs, implement against them deterministically, and report back — all without a single cloud API call.

Traditional AI-assisted development treats code as the primary artifact and specifications as loose markdown. SovereignSpec inverts this: specifications are living, graph-grounded knowledge artifacts with typed fields, dependency edges, version history, and automated contradiction detection. Every spec is a node in a knowledge graph that tracks what depends on what, which decisions created which architecture, and whether new specs drift from the project's founding constitution.

Code generation is not a free-form LLM call. SovereignSpec enforces GBNF grammar constraints on the local Ollama inference backend, producing output that is structurally valid by construction — no hallucinated syntax, no missing fields, no inconsistent APIs. The result is deterministic, reproducible implementation that matches the spec because the LLM physically cannot generate tokens outside the grammar's allowed token space.

SovereignSpec is agent-agnostic by design. It integrates with OpenCode, Claude Code, Cursor, Cline, RooCode, Codex CLI, Gemini CLI, Aider, Windsurf, Continue, and any file-aware coding agent — all through the filesystem, with zero custom plugins or API integrations. The `.sovereignspec/bootstrap.md` file is a universal contract that any agent can read to understand the project's rules, specs, tasks, and constraints.

---

## Why SovereignSpec Exists

The breakthrough concept of Spec-Driven Development was proven by GitHub's Spec Kit (108K+ stars), but Spec Kit has fundamental architectural limitations:

| Gap | Spec Kit | SovereignSpec |
|-----|----------|---------------|
| **Cloud dependency** | Every pipeline step (`/clarify`, `/plan`, `/implement`) calls external LLM endpoints | Zero cloud APIs — all inference via local Ollama |
| **RAG integration** | No vector search — specs are flat markdown, ungrounded in knowledge | ChromaDB-powered semantic search over all specs, ADRs, and patterns |
| **Grammar enforcement** | No output constraints — LLM can generate anything | GBNF grammars constrain token probability space for deterministic output |
| **Spec evolution tracking** | No version diffing, no drift detection | Full version history, semantic diffs, contradiction detection, drift scoring |
| **Knowledge graph** | No relationship modeling between specs | 11 node types, 9 edge types, graph queries for impact analysis |
| **Local-first** | Requires GitHub API and cloud LLMs | Runs entirely offline on your machine |

SovereignSpec fills the local-first SDD gap: the same powerful spec-driven workflow, zero cloud dependency, fully offline, fully deterministic.

---

## Architecture

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

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Local LLM | Ollama (Qwen, Llama 3.1, DeepSeek, Gemma, Mistral) |
| Vector Store | ChromaDB (local, embedded) |
| Metadata DB | SQLite (via better-sqlite3 or Drizzle ORM) |
| Graph Store | NetworkX (Python) / adjacency JSON (default), Neo4j (optional) |
| CLI | Python 3.11+ with Click or Typer |
| Grammar Enforcement | GBNF (llama-cpp grammar files) |
| Spec Format | .sspec (YAML-superset) |
| Package Manager | uv (Python) + pnpm (Node) |

---

## Quick Start

```bash
# 1. Install SovereignSpec
uv tool install sovereignspec --from git+https://github.com/kliewerdaniel/sovereignSpec.git

# 2. Initialize a project
sovereignspec init my-project
cd my-project

# 3. Establish governing principles
# Run this command in your agent's chat:
#   /sovereign.constitution
# Or use the CLI:
sovereignspec sovereign-constitution "Build a REST API with TypeScript, Express, and SQLite. No ORM. Functional programming style."

# 4. Define what to build
#   /sovereign.specify "JWT authentication with refresh tokens, role-based access control"

# 5. Full SDD pipeline
#   /sovereign.clarify → /sovereign.plan → /sovereign.tasks → /sovereign.implement
```

---

## CLI Command Reference

| Command | Description |
|---------|------------|
| `sovereignspec init [path]` | Initialize a new SovereignSpec project |
| `sovereignspec doctor` | Verify system health (Ollama, ChromaDB, SQLite) |
| `sovereignspec integrate --agent <name>` | Configure agent adapter for a supported coding agent |
| `sovereignspec spec create <spec-id>` | Create a new .sspec specification file |
| `sovereignspec spec validate <spec-id>\|--all` | Validate one or all specs against rules |
| `sovereignspec spec compile <spec-id>\|--all` | Compile spec into plans, tasks, docs, graph updates |
| `sovereignspec spec list [--status <s>]` | List specs, optionally filtered by lifecycle status |
| `sovereignspec spec diff <spec-id>` | Show semantic diff between spec versions |
| `sovereignspec spec graph <spec-id>` | Visualize spec's position in the knowledge graph |
| `sovereignspec sovereign-constitution [...]` | Create or update project governing principles |
| `sovereignspec specify [description]` | Define a new feature spec from a description |
| `sovereignspec clarify <spec-id>` | RAG-grounded clarification of a spec |
| `sovereignspec plan <spec-id>` | Generate technical implementation plan |
| `sovereignspec tasks <spec-id>` | Decompose plan into actionable tasks |
| `sovereignspec analyze <spec-id>\|--all` | Cross-spec consistency and contradiction analysis |
| `sovereignspec implement <spec-id>` | Execute implementation against spec constraints |
| `sovereignspec adr create` | Create a new Architecture Decision Record |
| `sovereignspec adr list` | List all ADRs |
| `sovereignspec context build <spec-id>` | Assemble agent context package |
| `sovereignspec graph query [--what-breaks]` | Execute knowledge graph queries |
| `sovereignspec memory sync` | Synchronize agent memory |
| `sovereignspec memory status` | Show memory store status |
| `sovereignspec repo map` | Generate repository intelligence map |
| `sovereignspec repo patterns` | Extract and display coding patterns |
| `sovereignspec agent list` | List registered agent sessions |
| `sovereignspec agent status <name>` | Show agent session details |
| `sovereignspec docs generate <spec-id>\|--all` | Generate documentation bundle |

---

## Spec File Format (.sspec)

```yaml
id: jwt-authentication
title: JWT Authentication System
version: 1.0.0
status: draft
purpose: Provide secure JWT-based authentication with access and refresh token flows.

requirements:
  - Users must authenticate with email and password
  - System issues short-lived access tokens (15 min) and long-lived refresh tokens (7 days)
  - Refresh tokens are single-use and rotated on each refresh
  - Role-based access control with admin, user, and viewer roles

constraints:
  - No third-party auth providers (Google, GitHub OAuth)
  - Tokens must be stateless (no server-side session store)
  - All secrets must be environment-variable configured
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

Every SovereignSpec project contains `.sovereignspec/bootstrap.md` — a universal contract file that any file-aware coding agent reads on startup. This file instructs the agent to:

1. Read `.sovereignspec/specs/` for active specifications
2. Read `.sovereignspec/adr/` for architectural decisions
3. Read `.sovereignspec/patterns/pattern_library.json` for coding conventions
4. Read `.sovereignspec/tasks/active_tasks.md` for current work units
5. Honor all constraints listed in active specs
6. Update implementation status upon task completion
7. Generate tests for every implemented feature
8. Generate documentation for every module changed
9. Update `.sovereignspec/graph/graph.json` with new relationships
10. Record all decisions as new ADR drafts in `.sovereignspec/adr/`

No custom plugin required. No API integration. Just a file on disk.

---

## Directory Structure

After `sovereignspec init`, a project looks like:

```
my-project/
├── .sovereignspec/
│   ├── config.json
│   ├── bootstrap.md
│   ├── constitution.md
│   ├── specs/
│   │   └── (your .sspec files)
│   ├── adr/
│   │   └── (ADR-NNN.md files)
│   ├── tasks/
│   │   └── (task lists per spec)
│   ├── patterns/
│   │   ├── pattern_library.json
│   │   └── repository_map.json
│   ├── memory/
│   │   └── (persistent agent memory blobs)
│   ├── graph/
│   │   └── graph.json
│   ├── agents/
│   │   └── (agent session records)
│   ├── grammar/
│   │   └── (GBNF grammar files)
│   ├── templates/
│   │   ├── spec-template.sspec
│   │   ├── adr-template.md
│   │   └── tasks-template.md
│   └── docs/
│       └── (auto-generated documentation)
├── (your source code)
└── (your project files)
```

---

## Understanding the Pipeline

The SovereignSpec pipeline is designed around the `/sovereign.*` command chain:

```
/sovereign.constitution → /sovereign.specify → /sovereign.clarify
→ /sovereign.plan → /sovereign.tasks → /sovereign.analyze
→ /sovereign.implement → /sovereign.checklist
```

Each command feeds into the next. The constitution grounds everything. Specs emerge from the constitution. Plans emerge from specs. Tasks emerge from plans. Implementation executes tasks. Analysis checks consistency across the entire graph. The checklist verifies quality.

At any point, you can run `/sovereign.analyze` to identify contradictions between specs, trace dependency chains, and measure narrative drift from the constitution.

---

## Supported Agents

SovereignSpec integrates with every major AI coding agent through filesystem conventions, no custom plugins required:

| Agent | Integration File | Mechanism |
|-------|-----------------|-----------|
| Claude Code | `CLAUDE.md` + `.claude/commands/*.md` | File-aware agent reads CLAUDE.md, discovers /sovereign.* commands |
| OpenCode | `AGENTS.md` | Agent reads AGENTS.md for project context and rules |
| Cursor | `.cursor/rules/*.mdc` | Cursor rule files with sovereign.* command templates |
| Cline | `.clinerules` | Custom instructions file with full contract |
| RooCode | `.roo/rules.md` | RooCode mode configuration with sovereign commands |
| Codex CLI | `AGENTS.md` + skills mode | Agent reads AGENTS.md, skills discoverable via /sovereign.* |
| Gemini CLI | `GEMINI.md` | Gemini-specific instruction file |
| Aider | `.aider.conf.yml` + system prompt injection | Configuration-based integration |
| Windsurf | `.windsurfrules` | Rules file with sovereign command definitions |
| Continue | `.continue/config.json` | Continue dev config with slash commands |
| Generic | `.sovereignspec/bootstrap.md` | Universal fallback — any file-aware agent |

---

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/kliewerdaniel/sovereignSpec.git
cd sovereignSpec
uv sync
uv run sovereignspec --help
```

### Key Development Principles

- **Local-first**: No feature should require a cloud API call to function
- **Agent-agnostic**: No code should assume a specific coding agent
- **Deterministic**: Given the same spec and constitution, the same output must result
- **Tested**: Every validation rule, graph operation, and adapter must have tests

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built by [Daniel Kliewer](https://danielkliewer.com). Specifications are the source of truth. Code is downstream.*

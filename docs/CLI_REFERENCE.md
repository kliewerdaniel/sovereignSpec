# SovereignSpec CLI Reference

**Version 1.0.0 — Complete Command Reference**

---

## Global Flags

| Flag | Env Variable | Description |
|------|-------------|-------------|
| `--project-dir PATH` | `SOVEREIGNSPEC_PROJECT_DIR` | Path to the project root (default: current directory) |
| `--model MODEL` | `SOVEREIGNSPEC_MODEL` | Override the generation model for this command |
| `--verbose` | | Enable verbose output (debug logging) |
| `--json` | | Output in machine-readable JSON format |
| `--help` | | Show help message |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SOVEREIGNSPEC_MODEL` | `qwen2.5-coder:32b` | Default generation model |
| `SOVEREIGNSPEC_OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `SOVEREIGNSPEC_DB_PATH` | `.sovereignspec/memory/sovereignspec.db` | SQLite database path |
| `SOVEREIGNSPEC_CHROMA_PATH` | `.sovereignspec/memory/chromadb` | ChromaDB persistence path |
| `SOVEREIGNSPEC_PROJECT_DIR` | `.` | Project root directory |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error |
| 2 | Compilation error |
| 3 | Ollama unavailable |
| 4 | Not a SovereignSpec project |
| 5 | Validation failed |

---

## Command Reference

### `sovereignspec init [path]`

Initialize a new SovereignSpec project.

**Usage:**
```bash
sovereignspec init [path] [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `path` | Directory to initialize (default: current directory) |

**Options:**
| Option | Description |
|--------|-------------|
| `--force` | Initialize in non-empty directory |
| `--model MODEL` | Specify default Ollama model |
| `--adapter ADAPTER` | Pre-configure agent adapter (claude-code, opencode, cursor, etc.) |

**Examples:**
```bash
sovereignspec init my-project
sovereignspec init .
sovereignspec init . --force
sovereignspec init . --model qwen2.5-coder:32b --adapter claude-code
```

**Output:**
Creates `.sovereignspec/` directory tree with config, templates, and grammar files.

---

### `sovereignspec doctor`

Verify system health.

**Usage:**
```bash
sovereignspec doctor [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repair` | Attempt repair of common issues |
| `--verbose` | Show detailed diagnostics |

**Output:**
```
✓ Python 3.11.7
✓ Ollama running (localhost:11434)
✓ Models: qwen2.5-coder:32b, nomic-embed-text
✓ ChromaDB available
✓ SQLite available
✓ File system writable
```

**JSON output** (with `--json`):
```json
{
  "status": "healthy",
  "checks": {
    "python": { "ok": true, "version": "3.11.7" },
    "ollama": { "ok": true, "models": ["qwen2.5-coder:32b"] },
    "chroma": { "ok": true },
    "sqlite": { "ok": true }
  }
}
```

---

### `sovereignspec integrate --agent <adapter>`

Configure agent adapter for a supported coding agent.

**Usage:**
```bash
sovereignspec integrate --agent <adapter> [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `--agent` | Adapter name: claude-code, opencode, cursor, cline, roocode, codex, gemini-cli, aider, windsurf, continue, generic |

**Options:**
| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing integration files |

**Examples:**
```bash
sovereignspec integrate --agent claude-code
sovereignspec integrate --agent opencode --force
```

**Output:**
Writes adapter-specific files to the project root (see docs/AGENT_INTEGRATION.md).

---

### `sovereignspec spec create <spec-id>`

Create a new .sspec specification file.

**Usage:**
```bash
sovereignspec spec create <spec-id> [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `spec-id` | Kebab-case spec identifier |

**Options:**
| Option | Description |
|--------|-------------|
| `--title TEXT` | Spec title |
| `--purpose TEXT` | Spec purpose |
| `--from-template` | Use the spec template as starting point |
| `--open` | Open in default editor |

**Examples:**
```bash
sovereignspec spec create jwt-authentication --title "JWT Authentication System"
sovereignspec spec create user-profile-api --from-template --open
```

**Output:**
Creates `specs/{spec-id}.sspec` with template content. Adds spec record to SQLite.

---

### `sovereignspec spec validate <spec-id> | --all`

Validate one or all specs against validation rules.

**Usage:**
```bash
sovereignspec spec validate <spec-id>
sovereignspec spec validate --all
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `spec-id` | Specific spec to validate |

**Options:**
| Option | Description |
|--------|-------------|
| `--all` | Validate all specs in the project |
| `--json` | Machine-readable validation report |
| `--strict` | Also check cross-spec contradictions (may invoke LLM) |

**Output:**
```
Validating jwt-authentication...
  ✓ MISSING_PURPOSE
  ✓ AMBIGUOUS_REQUIREMENTS
  ✓ UNDEFINED_DEPENDENCY
  ✓ MISSING_ACCEPTANCE_CRITERIA
  ✓ MISSING_TEST_CASES
  ✓ CONTRADICTS_EXISTING_SPEC
  ✓ DEPENDENCY_CYCLE
  ✓ NARRATIVE_DRIFT
  ✓ INCOMPLETE_SECURITY
  ✓ DUPLICATE_ID
  ✓ INVALID_STATUS_TRANSITION
  ✓ MISSING_CONSTRAINTS
  Result: VALID (12/12 rules passed)
```

---

### `sovereignspec spec compile <spec-id> | --all`

Compile spec into plans, tasks, docs, and graph updates.

**Usage:**
```bash
sovereignspec spec compile <spec-id>
sovereignspec spec compile --all
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `spec-id` | Specific spec to compile |

**Options:|
| Option | Description |
|--------|-------------|
| `--all` | Compile all active specs |
| `--rollback` | Roll back to previous version |
| `--skip-validation` | Skip validation step (use with caution) |
| `--dry-run` | Show what would be generated without writing |

**Output:**
```
Compiling jwt-authentication...
  [1/12] ✓ Parse .sspec YAML
  [2/12] ✓ Validate fields
  [3/12] ✓ Resolve dependency graph
  [4/12] ✓ Check contradictions
  [5/12] ✓ Compute drift score
  [6/12] ✓ Generate implementation plan
  [7/12] ✓ Generate task tree
  [8/12] ✓ Generate agent context
  [9/12] ✓ Generate documentation bundle
  [10/12] ✓ Update knowledge graph
  [11/12] ✓ Update ChromaDB
  [12/12] ✓ Commit version record
  Compilation complete. Version: 1.0.0 → 1.0.1
```

---

### `sovereignspec spec list [--status <status>]`

List specs, optionally filtered by lifecycle status.

**Usage:**
```bash
sovereignspec spec list [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--status STATUS` | Filter by status (draft, validated, approved, active, implemented, verified, archived) |

**Examples:**
```bash
sovereignspec spec list
sovereignspec spec list --status active
sovereignspec spec list --json
```

**Output:**
```
ID                     Title                           Status      Version
──────────────────────────────────────────────────────────────────────────
jwt-authentication     JWT Authentication System       draft       1.0.0
user-profile-api       User Profile CRUD API           draft       1.0.0
database-migration     Database Migration Workflow     draft       1.0.0
```

---

### `sovereignspec spec diff <spec-id> [--version v1] [--version v2]`

Show semantic diff between spec versions.

**Usage:**
```bash
sovereignspec spec diff <spec-id> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--version V1` | First version to compare (default: previous version) |
| `--version V2` | Second version to compare (default: current version) |

**Examples:**
```bash
sovereignspec spec diff jwt-authentication
sovereignspec spec diff jwt-authentication --version 1.0.0 --version 1.1.0
```

**Output:**
```
Diff: jwt-authentication v1.0.0 → v1.1.0
─────────────────────────────────────────
[REQUIREMENT ADDED]  + Users must verify email before first login
[REQUIREMENT REMOVED] - Rate limiting on /auth/login: 5 attempts per minute per IP
[CONSTRAINT ADDED]   + Email verification tokens expire after 24 hours
Drift score: 0.72 (was 0.68)
```

---

### `sovereignspec spec graph <spec-id>`

Visualize spec's position in the knowledge graph.

**Usage:**
```bash
sovereignspec spec graph <spec-id>
```

**Output:**
ASCII graph visualization:
```
spec:jwt-authentication
  ├── DEPENDS_ON ── spec:user-profile-api
  ├── REFERENCES ── adr:ADR-004
  ├── REFERENCES ── adr:ADR-006
  └── IMPLEMENTS ── feat:authentication-system

feat:authentication-system
  └── REFERENCES ── module:src/auth
```

---

### `sovereignspec sovereign-constitution [description]`

Create or update project governing principles.

**Usage:**
```bash
sovereignspec sovereign-constitution [description]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `description` | Plain-text description of the project's governing principles |

**Examples:**
```bash
sovereignspec sovereign-constitution "Build a REST API with TypeScript, Express, and SQLite. No ORM. Pure functional style."
```

**Output:**
```
Constitution generated and written to .sovereignspec/constitution.md
Drift baseline established. All new specs will be scored against this constitution.
```

---

### `sovereignspec specify [description]`

Define a new feature spec from a natural language description.

**Usage:**
```bash
sovereignspec specify [description]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `description` | Description of the feature to specify |

**Examples:**
```bash
sovereignspec specify "JWT authentication with refresh tokens and role-based access control"
```

**Output:**
```
Generating spec from description...
  LLM generated spec: jwt-authentication
  Purpose: Provide secure JWT-based authentication...
  Requirements: 7 requirements extracted
  Constraints: 6 constraints extracted
  Spec written to .sovereignspec/specs/jwt-authentication.sspec
  Status: draft. Run `sovereignspec spec validate jwt-authentication` to validate.
```

---

### `sovereignspec clarify <spec-id>`

RAG-grounded clarification of a spec.

**Usage:**
```bash
sovereignspec clarify <spec-id>
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `spec-id` | Spec ID to clarify |

**Output:**
Interactive Q&A session about the spec, grounded in:
- The spec's own content
- Related specs from ChromaDB similarity search
- Repository patterns
- Relevant ADRs

---

### `sovereignspec plan <spec-id> [--tech-stack "..."]`

Generate technical implementation plan.

**Usage:**
```bash
sovereignspec plan <spec-id> [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `spec-id` | Spec ID to plan |

**Options:**
| Option | Description |
|--------|-------------|
| `--tech-stack TEXT` | Override or supplement the tech stack description |

**Output:**
Writes implementation plan to `.sovereignspec/docs/{spec-id}/implementation.md`.

---

### `sovereignspec tasks <spec-id>`

Decompose plan into actionable task list.

**Usage:**
```bash
sovereignspec tasks <spec-id>
```

**Output:**
Writes task files:
- `.sovereignspec/tasks/{spec-id}-tasks.md` (human-readable)
- `.sovereignspec/tasks/{spec-id}-tasks.json` (machine-readable)

---

### `sovereignspec analyze <spec-id> | --all`

Cross-spec consistency and contradiction analysis.

**Usage:**
```bash
sovereignspec analyze <spec-id>
sovereignspec analyze --all
```

**Output:**
```
Analyzing jwt-authentication...
  Checking contradictions against active specs...
  ✓ user-profile-api: No contradiction
  ✗ rate-limiting: CONFLICT (score: 0.82)
    "jwt-authentication specifies 5 req/min rate limit, rate-limiting spec specifies 10 req/min"
  Dependency health: 1 of 1 dependencies are active
  Drift score: 0.72 (threshold: 0.6) ✓
  Recommendations:
    - Resolve rate limit conflict with rate-limiting spec
```

---

### `sovereignspec implement <spec-id>`

Execute implementation against spec constraints.

**Usage:**
```bash
sovereignspec implement <spec-id> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--agent AGENT` | Override agent adapter for this implementation |
| `--dry-run` | Show what would be implemented without generating code |

**Output:**
```
Implementing jwt-authentication...
  Generating context package for claude-code...
  Context package written to agent_context/jwt-authentication-context.md
  Agent tasks written to tasks/jwt-authentication-tasks.md
  Ready for agent. Run /sovereign.implement in Claude Code.
```

---

### `sovereignspec adr create [--title "..."] [--context "..."]`

Create a new Architecture Decision Record.

**Usage:**
```bash
sovereignspec adr create [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--title TEXT` | ADR title |
| `--context TEXT` | Brief context for the decision |

**Examples:**
```bash
sovereignspec adr create --title "Use SQLite as Primary Metadata Store" --context "Need local-first persistence without external DB"
```

**Output:**
```
ADR-006 created at .sovereignspec/adr/ADR-006.md
Status: proposed
```

---

### `sovereignspec adr list`

List all Architecture Decision Records.

**Output:**
```
#   Title                                    Status
─────────────────────────────────────────────────────
001 Local-First Architecture Decision        Accepted
002 Specification Graph Node Model           Accepted
003 GBNF Grammar Enforcement                 Accepted
004 ChromaDB for Vector Storage              Proposed
005 Agent Agnostic Bootstrap Protocol        Accepted
006 Use SQLite as Primary Metadata Store     Proposed
```

---

### `sovereignspec context build <spec-id> [--agent <adapter>]`

Assemble agent context package.

**Usage:**
```bash
sovereignspec context build <spec-id> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--agent ADAPTER` | Target agent adapter for context format |

**Output:**
```
Context package built for spec jwt-authentication:
  Agent: claude-code
  Sections:
    - Current spec (jwt-authentication)
    - Related specs (user-profile-api, rate-limiting)
    - Relevant ADRs (ADR-004, ADR-006)
    - Repository patterns (10 patterns)
    - Graph context (dependency chain)
    - Active tasks (5 tasks pending)
  Written to agent_context/jwt-authentication-context.md
```

---

### `sovereignspec graph query [--what-breaks spec-id] [--affects-module module-name]`

Execute knowledge graph queries.

**Usage:**
```bash
sovereignspec graph query --what-breaks <spec-id>
sovereignspec graph query --affects-module <module-path>
```

**Options:**
| Option | Description |
|--------|-------------|
| `--what-breaks SPEC_ID` | Find nodes affected if this spec changes |
| `--affects-module PATH` | Find specs that reference this module |

**Output:**
```
--what-breaks jwt-authentication:
  Affected nodes:
    - spec:user-profile-api (DEPENDS_ON, depth 1)
    - feat:authentication-system (IMPLEMENTS, depth 1)
    - mod:src/middleware/auth.ts (REFERENCES, depth 1)
    - task:auth-001 (IMPLEMENTS, depth 2)
```

---

### `sovereignspec memory sync`

Synchronize persistent memory stores.

**Usage:**
```bash
sovereignspec memory sync [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--rebuild-graph` | Rebuild graph.json from SQLite relationships |
| `--rebuild-embeddings` | Rebuild all ChromaDB embeddings from specs |

---

### `sovereignspec memory status`

Show memory store status.

**Output:**
```
Memory Store Status
──────────────────────
SQLite:    .sovereignspec/memory/sovereignspec.db (1.2 MB)
ChromaDB:  .sovereignspec/memory/chromadb/ (3 collections, 47 embeddings)
Graph:     .sovereignspec/graph/graph.json (8 nodes, 12 edges)
```

---

### `sovereignspec repo map`

Generate repository intelligence map.

**Usage:**
```bash
sovereignspec repo map [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--rebuild` | Force rebuild even if map exists |

**Output:**
```
Repository mapped:
  Languages: typescript (60%), python (25%), sql (4%)
  Modules: 12 modules detected
  Entrypoints: src/index.ts, api/app.py
  Patterns: 15 coding patterns extracted
  Written to .sovereignspec/patterns/repository_map.json
```

---

### `sovereignspec repo patterns`

Extract and display coding patterns.

**Output:**
```
Pattern Library
──────────────────────
naming:      camelCase functions, PascalCase classes
error:       Custom AppError class hierarchy
testing:     *.test.ts colocated with source
imports:     external → internal → relative
api-routes:  /api/v1/{resource} with middleware chains
```

---

### `sovereignspec agent list`

List registered agent sessions.

**Output:**
```
Agent Sessions
──────────────────────────────
claude-code   Last seen: 2025-01-15 10:30
opencode      Last seen: 2025-01-14 15:00
```

---

### `sovereignspec agent status <agent-name>`

Show agent session details.

**Usage:**
```bash
sovereignspec agent status <agent-name>
```

**Output:**
```
Agent: claude-code
  Adapter: claude-code
  Last seen: 2025-01-15 10:30:00
  Sessions: 3
  Artifacts submitted: 12 (12 validated ✓)
  Active tasks: 2
```

---

### `sovereignspec docs generate <spec-id> | --all`

Generate documentation bundle.

**Usage:**
```bash
sovereignspec docs generate <spec-id>
sovereignspec docs generate --all
```

**Options:**
| Option | Description |
|--------|-------------|
| `--format FORMAT` | Output format: markdown (default), html, pdf |
| `--open` | Open generated docs in browser |

**Output:**
```
Generating docs for jwt-authentication...
  ✓ docs/jwt-authentication/implementation.md
  ✓ docs/jwt-authentication/testing.md
  ✓ docs/jwt-authentication/api.md
  ✓ docs/jwt-authentication/deployment.md
Done. 4 files generated.
```

# SovereignSpec Architecture

**Version 1.0.0 — Complete System Architecture Document**

---

## 1. System Overview and Design Philosophy

SovereignSpec is a seven-layer architecture designed around five core principles. Each layer has a single responsibility, communicates with adjacent layers through well-defined interfaces, and can be replaced independently.

### 1.1 Five Core Principles

#### Principle 1: Local First

Everything runs on your machine. No inference request ever leaves the local network. All data — specifications, embeddings, knowledge graph, repository maps, agent memory — is stored in local files and databases. ChromaDB runs embedded in the Python process. SQLite is a local file. Ollama serves models on localhost. The Next.js UI runs on localhost. Network connectivity is required only for initial installation and model downloads.

This principle eliminates three systemic risks of cloud-dependent SDD: data leakage (specs never leave your machine), latency (inference completes in milliseconds on local hardware), and cost (no per-token billing). It also enables air-gap operation for classified or proprietary codebases.

The trade-off is computational: local models require sufficient RAM and GPU/accelerator. The minimum configuration (Mistral 7B via Ollama on CPU) runs 5-10 tokens/second — slow enough to notice but fast enough for a compile-check-clarify workflow. The recommended configuration (Qwen 2.5 Coder 32B on a Mac with 64GB+ RAM) runs at interactive speed.

#### Principle 2: Agent Agnostic

SovereignSpec never assumes a specific coding agent. Every integration happens through the filesystem: SovereignSpec writes files that agents read; agents write files that SovereignSpec reads. There is no API integration, no plugin system, no custom protocol. The `.sovereignspec/bootstrap.md` file is the universal contract — any file-aware coding agent can read it and understand the project's rules, regardless of whether the agent knows about SovereignSpec.

This principle ensures that SovereignSpec does not need to track the rapidly evolving capabilities of individual coding agents. When a new agent emerges, integration is a matter of writing one file in that agent's convention. When an agent changes its behavior, no SovereignSpec code changes — only the files it writes for that agent.

#### Principle 3: Specification As Source

The `.sspec` file is the source of truth. Not the code, not the README, not the comments. Code is generated from specs, validated against specs, and disposable in favor of specs. If code and spec disagree, the spec wins — regenerate the code.

This inverts the traditional development model where code accumulates authority over time through maintenance and debugging history. In SovereignSpec, specs are the durable artifact. They are versioned, validated, graph-grounded, and tested. Code is ephemeral — it can be regenerated from spec at any time, which is why every spec includes acceptance criteria and test cases that define correct implementation independently of any particular codebase.

#### Principle 4: Sovereign Memory

SovereignSpec maintains its own persistent memory store that is independent of any agent's context window. The memory store contains spec versions, relationship data, contradiction reports, drift history, agent session records, and artifact registrations. This memory persists across projects, across agent sessions, and across model upgrades.

The memory layer is what enables SovereignSpec to detect contradictions and drift that span multiple agent sessions. An agent might not remember a spec it implemented three sessions ago, but the knowledge graph does, and the contradiction detector will flag the conflict.

#### Principle 5: Deterministic Development

Given the same specification and constitution, SovereignSpec produces the same outputs. This is achieved through GBNF grammar constraints that restrict the local LLM's token probability space to valid structures only. The grammar files at `.sovereignspec/grammar/*.gbnf` define the exact schema for implementation plans, task lists, API specs, and ADRs. The LLM physically cannot generate tokens outside the grammar's allowed token space.

Determinism means that regenerating implementation from a spec produces comparable results across runs, across model versions, and (within the same model) across machines. This makes SovereignSpec suitable for CI/CD pipelines where generated output must be predictable.

### 1.2 Contrast with Vibe Coding

Vibe coding (iterative prompting without formal specifications) suffers from:

| Problem | Impact | SovereignSpec Solution |
|---------|--------|----------------------|
| Hallucination rate | 30-60% of generated code contains subtle bugs | GBNF grammar enforces structural validity; specs define acceptance criteria |
| Rework cycles | 5-15 iterations per feature due to misalignment | Spec-driven alignment in one pass |
| Scalability | Breaks down beyond 3-5 files | Knowledge graph tracks 1000+ node relationships |
| Knowledge retention | Agent forgets context every session | Sovereign memory persists across sessions |
| Consistency | Different agents produce incompatible code | Shared spec graph enforces consistency |

### 1.3 Contrast with Spec Kit

Spec Kit (github/spec-kit) proved SDD works at scale but has architectural limitations:

| Gap | Spec Kit | SovereignSpec |
|-----|----------|---------------|
| **Cloud dependency** | `/clarify`, `/plan`, `/implement` call external LLM endpoints via GitHub Models API | Zero cloud APIs — all inference via local Ollama on localhost:11434 |
| **RAG integration** | No vector search — specs are flat markdown, ungrounded in repository knowledge | ChromaDB with all-spec embeddings; semantic retrieval for clarification and planning |
| **Grammar enforcement** | No output constraints — LLM generates free-form text that may miss fields | GBNF grammar files constrain every output type to a defined schema |
| **Spec evolution** | No version tracking; specs are static files with git history only | Full version history in SQLite; semantic diffing; contradiction detection; drift scoring |
| **Knowledge graph** | No relationship model — spec dependencies are implicit | Directed graph with 11 node types and 9 edge types; queryable for impact analysis |
| **Local-first** | Requires GitHub API token and cloud LLM credits | Fully offline after initial setup |

---

## 2. Layer 1 — Local Infrastructure

### 2.1 Ollama Integration

Ollama serves as the local inference backend. SovereignSpec communicates with Ollama through its REST API at `http://localhost:11434`.

**Model Management:**
- Models are configured in `.sovereignspec/config.json` under `models` key
- Separate models can be specified for different tasks (embeddings vs. generation vs. analysis)
- Model loading: `ollama pull <model>` on first use; SovereignSpec checks availability via `ollama list`
- Streaming: SovereignSpec supports streaming responses for long generation tasks (spec clarification, implementation)
- Non-streaming: Used for structured outputs where GBNF grammar is applied

**Ollama API Calls:**

```python
import requests
import json

# Text generation with GBNF grammar
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen2.5-coder:32b",
    "prompt": "Generate implementation plan for JWT authentication...",
    "format": "json",  # or stream: false
    "options": {
        "temperature": 0.1,
        "top_p": 0.9,
        "grammar": load_grammar_file(".sovereignspec/grammar/implementation_plan.gbnf")
    }
})

# Embeddings for semantic search
response = requests.post("http://localhost:11434/api/embeddings", json={
    "model": "nomic-embed-text",
    "prompt": "JWT authentication with refresh tokens..."
})
```

**Configuration** (in `.sovereignspec/config.json`):
```json
{
  "models": {
    "generation": "qwen2.5-coder:32b",
    "embeddings": "nomic-embed-text",
    "analysis": "llama3.1:70b"
  },
  "ollama": {
    "host": "http://localhost:11434",
    "timeout": 120,
    "stream": false
  }
}
```

### 2.2 ChromaDB

ChromaDB provides local, embedded vector storage for semantic search across specs, ADRs, and patterns.

**Collection Design:**
- Collection `sovereignspec_specs`: Embeds full `.sspec` content for semantic spec search
- Collection `sovereignspec_adrs`: Embeds ADR content for architectural decision search
- Collection `sovereignspec_patterns`: Embeds coding pattern descriptions for pattern matching

**Embedding Strategy:**
- Embedding model: `nomic-embed-text` (via Ollama) or `all-MiniLM-L6-v2` (via sentence-transformers)
- Chunking: Specs are chunked by section (purpose, requirements, constraints) with 512-token overlap
- Metadata stored per chunk: spec_id, section, version, status

**Distance Metrics:**
- Default: cosine similarity
- Fallback: L2 (euclidean) for exact-match queries

**Persistence:**
- ChromaDB persistence path: `.sovereignspec/memory/chromadb/`
- Auto-loaded on SovereignSpec startup
- Rebuilt on `sovereignspec memory sync`

### 2.3 SQLite Schema

The SQLite database at `.sovereignspec/memory/sovereignspec.db` stores all metadata.

#### Table: `projects`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| name | TEXT | NOT NULL | Human-readable project name |
| slug | TEXT | NOT NULL UNIQUE | URL-safe project identifier |
| constitution_path | TEXT | NOT NULL | Path to constitution.md |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | ISO 8601 |
| updated_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | ISO 8601 |
| status | TEXT | NOT NULL DEFAULT 'active' | active|archived|frozen |

#### Table: `specifications`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| project_id | TEXT | NOT NULL REFERENCES projects(id) | Parent project |
| spec_id | TEXT | NOT NULL | Kebab-case spec identifier |
| title | TEXT | NOT NULL | Human-readable title |
| status | TEXT | NOT NULL DEFAULT 'draft' | draft|validated|approved|active|implemented|verified|archived |
| file_path | TEXT | NOT NULL | Path to .sspec file |
| version | TEXT | NOT NULL DEFAULT '1.0.0' | Semver |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| updated_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| checksum | TEXT | NOT NULL | SHA-256 of file content |
| parent_id | TEXT | REFERENCES specifications(id) | For superseded specs |

Index: `CREATE INDEX idx_specifications_project ON specifications(project_id);`
Index: `CREATE INDEX idx_specifications_status ON specifications(status);`
Unique: `CREATE UNIQUE INDEX idx_specifications_spec_id ON specifications(project_id, spec_id);`

#### Table: `spec_relationships`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| source_spec_id | TEXT | NOT NULL REFERENCES specifications(id) | Source node |
| target_spec_id | TEXT | NOT NULL REFERENCES specifications(id) | Target node |
| relationship_type | TEXT | NOT NULL | DEPENDS_ON|IMPLEMENTS|REFERENCES|SUPERSEDES|CONFLICTS_WITH|RELATED_TO|VALIDATES |
| weight | REAL | NOT NULL DEFAULT 1.0 | Relationship strength (0.0-1.0) |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| metadata_json | TEXT | DEFAULT '{}' | Arbitrary metadata |

Index: `CREATE INDEX idx_relationships_source ON spec_relationships(source_spec_id);`
Index: `CREATE INDEX idx_relationships_target ON spec_relationships(target_spec_id);`

#### Table: `spec_versions`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| spec_id | TEXT | NOT NULL REFERENCES specifications(id) | Parent specification |
| version | TEXT | NOT NULL | Semver version |
| content_hash | TEXT | NOT NULL | SHA-256 of spec content at this version |
| diff_summary | TEXT | DEFAULT '' | Human-readable summary of changes |
| contradictions_json | TEXT | DEFAULT '[]' | Known contradictions at this version |
| drift_score | REAL | DEFAULT NULL | Narrative drift score (0.0-1.0, NULL if not computed) |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |

Index: `CREATE INDEX idx_spec_versions ON spec_versions(spec_id, version);`

#### Table: `adrs`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| project_id | TEXT | NOT NULL REFERENCES projects(id) | Parent project |
| number | INTEGER | NOT NULL | ADR sequence number |
| title | TEXT | NOT NULL | ADR title |
| status | TEXT | NOT NULL DEFAULT 'proposed' | proposed|accepted|deprecated|superseded |
| file_path | TEXT | NOT NULL | Path to ADR markdown file |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| superseded_by | INTEGER | DEFAULT NULL | ADR number that superseded this one |

Unique: `CREATE UNIQUE INDEX idx_adrs_number ON adrs(project_id, number);`

#### Table: `tasks`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| spec_id | TEXT | NOT NULL REFERENCES specifications(id) | Parent spec |
| title | TEXT | NOT NULL | Task title |
| status | TEXT | NOT NULL DEFAULT 'pending' | pending|in_progress|completed|blocked|failed |
| agent_id | TEXT | REFERENCES agents(id) | Assigned agent |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| completed_at | TEXT | DEFAULT NULL | |
| output_path | TEXT | DEFAULT NULL | Path to generated output |

Index: `CREATE INDEX idx_tasks_spec ON tasks(spec_id);`
Index: `CREATE INDEX idx_tasks_status ON tasks(status);`

#### Table: `agents`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| name | TEXT | NOT NULL | Agent display name |
| adapter_type | TEXT | NOT NULL | claude-code|opencode|cursor|cline|roocode|codex|gemini-cli|aider|windsurf|continue|generic |
| last_seen | TEXT | DEFAULT CURRENT_TIMESTAMP | |
| capabilities_json | TEXT | DEFAULT '{}' | Agent capability flags |

#### Table: `artifacts`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| task_id | TEXT | NOT NULL REFERENCES tasks(id) | Parent task |
| artifact_type | TEXT | NOT NULL | code|test|doc|config|migration|other |
| file_path | TEXT | NOT NULL | Path to artifact file |
| validated | INTEGER | NOT NULL DEFAULT 0 | 0=unvalidated, 1=passed, 2=failed |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |

Index: `CREATE INDEX idx_artifacts_task ON artifacts(task_id);`

#### Table: `patterns`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| project_id | TEXT | NOT NULL REFERENCES projects(id) | Parent project |
| pattern_type | TEXT | NOT NULL | naming|error-handling|testing|import|api-route|architecture|other |
| name | TEXT | NOT NULL | Pattern name |
| example | TEXT | NOT NULL | Code example illustrating the pattern |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |

Index: `CREATE INDEX idx_patterns_type ON patterns(pattern_type);`

#### Table: `sessions`
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | TEXT | PRIMARY KEY | UUID |
| project_id | TEXT | NOT NULL REFERENCES projects(id) | Parent project |
| agent_id | TEXT | REFERENCES agents(id) | Agent in session |
| started_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| ended_at | TEXT | DEFAULT NULL | |
| context_hash | TEXT | DEFAULT NULL | SHA-256 of context provided to agent |

### 2.4 File Watcher Design

SovereignSpec includes an optional file watcher that monitors `.sovereignspec/specs/` for changes and triggers re-validation.

**Implementation:**
- Python: `watchdog` library observer
- Event debounce: 500ms debounce interval to avoid re-validation on partial writes
- Triggers:
  - `specs/*.sspec` modified → re-validate + re-embed single spec
  - `specs/*.sspec` created → compile new spec
  - `specs/*.sspec` deleted → archive spec in database
  - `constitution.md` modified → re-compute drift scores for all active specs
  - `graph/graph.json` modified → reload graph into memory

**Configuration:**
```json
{
  "watcher": {
    "enabled": true,
    "debounce_ms": 500,
    "watch_dirs": ["specs", "adr", "constitution.md"]
  }
}
```

---

## 3. Layer 2 — Persistence Layer

### 3.1 Specification Storage Protocol

**File Format:**
- Specs are stored as `.sspec` files (YAML superset) in `.sovereignspec/specs/`
- File naming: `{spec-id}.sspec` (e.g., `jwt-authentication.sspec`)
- Encoding: UTF-8

**Versioning Strategy:**
- Every `sovereignspec spec compile` creates a new version record in `spec_versions`
- Versions follow semver: major for breaking requirement changes, minor for additions, patch for clarifications
- The `version` field in the `.sspec` file header is auto-incremented on compile
- Previous versions remain in the database for diff and rollback

**Checksum Computation:**
- SHA-256 of the raw `.sspec` file bytes
- Stored in `specifications.checksum` and `spec_versions.content_hash`
- Used for tamper detection: if checksum doesn't match on load, the file has been modified outside the compiler

**Diff Generation:**
- Line-level diff using Python's `difflib.unified_diff`
- Semantic diff that understands `.sspec` structure (field-level changes, requirement additions/removals)
- Diff summary stored in `spec_versions.diff_summary` as a human-readable string

### 3.2 ADR Storage

- ADRs are stored as markdown files at `.sovereignspec/adr/ADR-NNN.md`
- Numbering is sequential across the project (not per spec)
- Each ADR links to relevant specs via the `related_specs` frontmatter field
- ADRs are indexed in the `adrs` SQLite table

### 3.3 Task Storage

Tasks use a dual-write strategy:
1. **JSON** (`.sovereignspec/tasks/{spec-id}-tasks.json`): Machine-readable for SovereignSpec CLI
2. **Markdown** (`.sovereignspec/tasks/{spec-id}-tasks.md`): Human-readable for coding agents

Both files are generated by `sovereignspec tasks <spec-id>` and must be kept in sync. The agent reads the markdown version; SovereignSpec reads the JSON version for analysis.

### 3.4 Artifact Registry

All agent-generated outputs are tracked in:

`.sovereignspec/agents/{agent-name}/artifacts.json`

Schema:
```json
{
  "$schema": "sovereignspec-artifact-registry",
  "agent": "claude-code",
  "project": "my-project",
  "artifacts": [
    {
      "id": "artifact-uuid",
      "task_id": "task-uuid",
      "artifact_type": "code",
      "file_path": "src/auth/jwt.ts",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## 4. Layer 3 — Repository Intelligence

### 4.1 Repository Mapping Algorithm

The `sovereignspec repo map` command analyzes the source code repository to create a structured map of the codebase.

**Algorithm:**
1. Walk directory tree from project root, respecting `.gitignore`
2. For each file:
   a. Determine language from file extension
   b. Classify file type: source, test, config, documentation, build, data
   c. Detect entrypoints: files named `main.*`, `index.*`, `app.*`
   d. Detect framework conventions: Next.js pages, Express routes, Django views
3. Identify module boundaries: directories containing `package.json`, `__init__.py`, `Cargo.toml`, etc.
4. Detect dependency relationships: imports/requires across files
5. Output structured map to `.sovereignspec/patterns/repository_map.json`

**`repository_map.json` Schema:**
```json
{
  "$schema": "sovereignspec-repository-map",
  "project_name": "my-project",
  "analyzed_at": "2025-01-15T10:00:00Z",
  "language_stats": {
    "typescript": { "files": 45, "lines": 12000, "percentage": 60.0 },
    "python": { "files": 20, "lines": 5000, "percentage": 25.0 },
    "sql": { "files": 5, "lines": 800, "percentage": 4.0 }
  },
  "entrypoints": [
    { "path": "src/index.ts", "language": "typescript", "type": "app-entry" },
    { "path": "api/app.py", "language": "python", "type": "api-entry" }
  ],
  "modules": [
    {
      "path": "src/auth",
      "language": "typescript",
      "type": "module",
      "entrypoint": "src/auth/index.ts",
      "dependencies": ["src/common", "src/db"],
      "file_count": 8
    }
  ],
  "files": [
    {
      "path": "src/auth/jwt.ts",
      "language": "typescript",
      "type": "source",
      "imports": ["jsonwebtoken", "../common/errors"],
      "exports": ["signToken", "verifyToken", "refreshToken"],
      "size_bytes": 4096
    }
  ]
}
```

### 4.2 Pattern Extraction

Pattern extraction identifies coding conventions from the existing codebase.

**Detection Strategies:**

| Pattern Type | Detection Method | Example Output |
|-------------|-----------------|----------------|
| Naming conventions | Regex on file/code identifiers | `camelCase` for functions, `PascalCase` for classes |
| Error handling | AST pattern matching | `try/catch` blocks with custom error classes |
| Test file patterns | File naming analysis | `*.test.ts` colocated with source, `describe/it` blocks |
| Import organization | Import statement analysis | Groups: external → internal → relative |
| API route conventions | Route definition analysis | `/api/v1/{resource}` pattern, middleware chains |
| Database patterns | Query/ORM usage analysis | Raw SQL via `better-sqlite3`, no ORM |

Patterns are stored in `.sovereignspec/patterns/pattern_library.json`:

```json
{
  "$schema": "sovereignspec-pattern-library",
  "patterns": [
    {
      "id": "pattern-001",
      "type": "naming",
      "name": "function-naming-convention",
      "description": "All functions use camelCase naming",
      "example": "function getUserById(id: string): User { ... }",
      "files_matching": ["src/**/*.ts"],
      "confidence": 0.95
    },
    {
      "id": "pattern-002",
      "type": "error-handling",
      "name": "custom-error-classes",
      "description": "All errors extend AppError base class with statusCode and code fields",
      "example": "class NotFoundError extends AppError { statusCode = 404; ... }",
      "pattern_source": "ast-analysis",
      "confidence": 0.88
    }
  ]
}
```

### 4.3 Semantic Search Query Pipeline

The ChromaDB-based RAG pipeline works as follows:

1. **Query**: Natural language question or spec snippet (e.g., "How do we handle authentication errors?")
2. **Embed**: Generate embedding using `nomic-embed-text` via Ollama
3. **Retrieve**: Query ChromaDB collections for top-5 most similar documents
4. **Rank**: Score results by cosine similarity; filter below threshold (0.6)
5. **Format**: Assemble retrieved documents into a context block for the LLM prompt

**Example Queries and Retrieval Behavior:**

| Query | Retrieved From | Expected Result |
|-------|---------------|----------------|
| "How is JWT authentication implemented?" | specs (jwt-authentication) + patterns (auth patterns) | Full auth spec + relevant code patterns |
| "What decisions led to using SQLite?" | adrs (ADR-006) | ADR-006 with rationale and alternatives |
| "Are there any specs about rate limiting?" | specs + patterns | All specs containing rate limiting requirements |
| "Show me error handling patterns" | patterns (error-handling) | Top 3 error handling patterns with examples |

---

## 5. Layer 4 — Knowledge Graph

### 5.1 Node Types (11 types)

| Node Type | ID Prefix | Description | Creation Rule |
|-----------|-----------|-------------|---------------|
| Project | `proj-` | The SovereignSpec project itself | Created on `sovereignspec init` |
| Feature | `feat-` | A user-facing feature | Created on `/sovereign.specify` |
| Specification | `spec-` | A `.sspec` file | Created on `sovereignspec spec create` |
| Module | `mod-` | A source code module | Created on `sovereignspec repo map` |
| Service | `svc-` | A deployable service/component | Created on spec compilation with service hint |
| Endpoint | `ep-` | An API endpoint | Created on spec compilation (API specs) |
| Database | `db-` | A database or table | Created on spec compilation (data specs) |
| ADR | `adr-` | An Architecture Decision Record | Created on `sovereignspec adr create` |
| Task | `task-` | An implementation task | Created on `sovereignspec tasks` |
| Agent | `agt-` | A coding agent session | Created on first agent interaction |
| Document | `doc-` | A generated documentation file | Created on `sovereignspec docs generate` |

### 5.2 Relationship Types (9 types)

| Relationship | Direction | Weight Semantics | Description |
|-------------|-----------|-----------------|-------------|
| `IMPLEMENTS` | Task → Spec | 1.0 if complete | Task implements the spec's requirements |
| `DEPENDS_ON` | Spec → Spec | 1.0 | Spec A cannot be implemented before Spec B |
| `REFERENCES` | Spec → ADR | 0.5 | Spec refers to ADR for architectural context |
| `GENERATES` | Spec → Document | 1.0 | Spec compilation produced this document |
| `REPLACES` | Spec → Spec | 1.0 | New spec replaces old spec (old → archived) |
| `SUPERSEDES` | ADR → ADR | 1.0 | New ADR supersedes old ADR |
| `CONFLICTS_WITH` | Spec → Spec | 0.3-0.9 | Specs have contradictory requirements (weight = contradiction severity) |
| `RELATED_TO` | Spec → Spec | 0.3 | Specs share context but no hard dependency |
| `VALIDATES` | Test → Spec | 1.0 | Test validates the spec's acceptance criteria |

### 5.3 Graph Storage: Adjacency JSON (Default)

The default graph storage format requires zero external dependencies:

```json
{
  "project_id": "proj-uuid",
  "updated_at": "2025-01-15T10:00:00Z",
  "nodes": [
    {
      "id": "spec-jwt-authentication",
      "type": "Specification",
      "metadata": {
        "title": "JWT Authentication System",
        "status": "active",
        "version": "1.0.0",
        "file_path": ".sovereignspec/specs/jwt-authentication.sspec"
      }
    },
    {
      "id": "mod-auth-service",
      "type": "Module",
      "metadata": {
        "path": "src/auth",
        "language": "typescript"
      }
    }
  ],
  "edges": [
    {
      "source": "spec-jwt-authentication",
      "target": "mod-auth-service",
      "type": "REFERENCES",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "spec-user-profile-api",
      "type": "DEPENDS_ON",
      "weight": 1.0,
      "metadata": {}
    }
  ]
}
```

### 5.4 Neo4j Optional Upgrade Path

When `config.json` sets `"graph.store": "neo4j"`, SovereignSpec connects to a local Neo4j instance:

```json
{
  "graph": {
    "store": "neo4j",
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "password": "env:NEO4J_PASSWORD"
    }
  }
}
```

**Cypher Query Equivalents:**

| Adjacency JSON Operation | Cypher Equivalent |
|-------------------------|-------------------|
| `add_node(id, type, metadata)` | `CREATE (n:NodeType {id: $id, ...$metadata})` |
| `add_edge(source, target, type, weight)` | `MATCH (s {id: $source}), (t {id: $target}) CREATE (s)-[r:REL_TYPE {weight: $weight}]->(t)` |
| `what_breaks_if_changed(spec_id)` | `MATCH (s {id: $spec_id})-[*1..3]->(affected) RETURN affected` |
| `dependency_chain(spec_id)` | `MATCH path = (s {id: $spec_id})-[:DEPENDS_ON*]->(deps) RETURN path` |

### 5.5 NetworkX Python Bridge

When using adjacency JSON, graph operations use NetworkX:

```python
import networkx as nx
import json

with open(".sovereignspec/graph/graph.json") as f:
    data = json.load(f)

G = nx.DiGraph()

for node in data["nodes"]:
    G.add_node(node["id"], type=node["type"], **node["metadata"])

for edge in data["edges"]:
    G.add_edge(edge["source"], edge["target"],
               type=edge["type"], weight=edge["weight"])
```

### 5.6 Graph Query API

**`what_breaks_if_changed(spec_id)`**
Returns all nodes that would be affected if the given spec is modified, traversing DEPENDS_ON and REFERENCES edges up to depth 3.

```python
def what_breaks_if_changed(spec_id: str) -> list[Node]:
    descendants = nx.descendants_at_distance(G, spec_id, distance=3)
    return [nodes[n] for n in descendants if G.has_edge(spec_id, n)]
```

**`what_specs_affect_module(module_id)`**
Returns all specs that reference or depend on a given module.

```python
def what_specs_affect_module(module_id: str) -> list[Specification]:
    predecessors = list(G.predecessors(module_id))
    return [nodes[n] for n in predecessors if nodes[n]["type"] == "Specification"]
```

**`which_adr_created_architecture(pattern_name)`**
Find ADRs that resulted in a specific architectural pattern.

```python
def which_adr_created_architecture(pattern_name: str) -> list[ADR]:
    # Find specs matching the pattern, then trace back to ADRs via REFERENCES
    matching_specs = [n for n, d in nodes.items()
                      if d["type"] == "Specification"
                      and pattern_name in str(d)]
    adrs = []
    for spec_id in matching_specs:
        for pred in G.predecessors(spec_id):
            if nodes[pred]["type"] == "ADR":
                adrs.append(pred)
    return adrs
```

**`dependency_chain(spec_id, depth)`**
Returns the full dependency tree for a spec as a nested structure.

```python
def dependency_chain(spec_id: str, depth: int = 5) -> dict:
    if depth == 0:
        return {"id": spec_id, "dependencies": []}
    deps = [dependency_chain(n, depth - 1)
            for n in G.successors(spec_id)
            if G.edges[spec_id, n].get("type") == "DEPENDS_ON"]
    return {"id": spec_id, "dependencies": deps}
```

### 5.7 Spec Contradiction Detection Algorithm

```python
def detect_contradictions(spec_id: str, graph: KnowledgeGraph, chroma: ChromaClient, ollama: OllamaClient) -> list[ContradictionPair]:
    """
    1. Load the target spec
    2. Find related specs via ChromaDB similarity search
    3. For each related spec, prompt the LLM with GBNF-constrained output
       to score contradiction likelihood
    4. Store contradictions with score >= 0.7 in spec_relationships table
    """
    # Step 1: Embed the target spec
    target_spec = load_spec(spec_id)
    target_embedding = ollama.embed(target_spec.content)

    # Step 2: Find related specs via ChromaDB
    results = chroma.query(
        collection="sovereignspec_specs",
        query_embedding=target_embedding,
        n_results=10
    )

    contradictions = []
    grammar = load_grammar("grammar/contradiction_report.gbnf")

    for related_id in results.ids:
        if related_id == spec_id:
            continue

        related_spec = load_spec(related_id)

        # Step 3: Prompt LLM with grammar constraint
        prompt = f"""
        Analyze these two specifications for contradictions:

        SPEC A ({spec_id}):
        {target_spec.requirements}
        {target_spec.constraints}
        {target_spec.acceptance_criteria}

        SPEC B ({related_id}):
        {related_spec.requirements}
        {related_spec.constraints}
        {related_spec.acceptance_criteria}

        Output a contradiction report.
        """

        response = ollama.generate(prompt, grammar=grammar)
        report = parse_contradiction_report(response)

        if report.contradiction_score >= 0.7:
            contradiction = ContradictionPair(
                spec_a=spec_id,
                spec_b=related_id,
                score=report.contradiction_score,
                description=report.description,
                affected_fields=report.affected_fields
            )
            contradictions.append(contradiction)

            # Step 4: Store in graph
            graph.add_edge(
                source=spec_id,
                target=related_id,
                type="CONFLICTS_WITH",
                weight=report.contradiction_score,
                metadata={"description": report.description}
            )

    return contradictions
```

### 5.8 Narrative Drift Tracking Algorithm

```python
def compute_drift_score(spec_id: str, constitution_path: str, chroma: ChromaClient, ollama: OllamaClient) -> float:
    """
    1. Load the project constitution
    2. Load the target spec
    3. Embed both via Ollama
    4. Compute cosine similarity
    5. Convert to drift score (1.0 = aligned, 0.0 = completely drifted)
    6. Flag specs with drift_score < 0.6 for review
    """
    # Step 1: Load constitution
    with open(constitution_path) as f:
        constitution = f.read()

    # Step 2: Load spec
    spec = load_spec(spec_id)

    # Step 3: Embed both
    constitution_embedding = ollama.embed(constitution)
    spec_embedding = ollama.embed(
        f"{spec.purpose}\n{spec.requirements}\n{spec.constraints}"
    )

    # Step 4: Compute cosine similarity
    similarity = cosine_similarity(constitution_embedding, spec_embedding)

    # Step 5: Drift score
    drift_score = max(0.0, similarity)

    # Step 6: Flag if below threshold
    if drift_score < 0.6:
        logger.warning(f"Spec {spec_id} has high narrative drift (score: {drift_score:.2f})")

    return drift_score
```

---

## 6. Layer 5 — Specification Engine

### 6.1 .sspec File Format

Complete field specification is in [docs/SPECIFICATION_FORMAT.md](docs/SPECIFICATION_FORMAT.md).

### 6.2 Spec Compiler Pipeline

The compiler is invoked by `sovereignspec spec compile <spec-id>`:

```
┌─────────┐   ┌──────────┐   ┌───────────────┐   ┌──────────────┐
│ Parse   │──▶│ Validate │──▶│ Resolve deps   │──▶│ Check        │
│ .sspec  │   │ Fields   │   │ (topo sort)    │   │ Contradictions│
└─────────┘   └──────────┘   └───────────────┘   └──────────────┘
                                                       │
                                                       ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────────┐
│ Generate │◀──│ Generate │◀──│ Generate      │◀──│ Compute      │
│ Docs     │   │ Agent    │   │ Task Tree     │   │ Drift Score  │
│ Bundle   │   │ Context  │   │ (tasks.md)    │   │              │
└──────────┘   └──────────┘   └──────────────┘   └──────────────┘
     │
     ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│ Update   │──▶│ Update       │──▶│ Commit       │
│ KG       │   │ ChromaDB     │   │ Version      │
│ (graph)  │   │ (embeddings) │   │ (SQLite)     │
└──────────┘   └──────────────┘   └──────────────┘
```

**Step details:**

1. **Parse .sspec YAML**: Parse the `.sspec` file into a `Specification` Pydantic model. Raise `SpecParseError` on YAML syntax errors.

2. **Validate required fields**: Apply all 12 validation rules (Section 6.4).

3. **Resolve dependency graph**: Load all specs linked via `dependencies[]`, build directed graph, topological sort to determine implementation order. Detect cycles (rule DEPENDENCY_CYCLE).

4. **Check contradictions**: Run contradiction detection against in-graph specs (Section 5.7).

5. **Compute drift score**: Run narrative drift tracking against constitution (Section 5.8).

6. **Generate implementation plan**: Prompt local LLM with spec content + repository context + GBNF grammar for plan output.

7. **Generate task tree**: Decompose plan into individual tasks with dependencies, parallel markers.

8. **Generate agent context package**: Assemble `agent_context.md` with spec, related specs, ADRs, patterns, graph context.

9. **Generate documentation bundle**: Create `/docs/` markdown files.

10. **Update knowledge graph**: Add spec as node, create edges from dependencies.

11. **Update ChromaDB**: Generate embeddings, upsert into collections.

12. **Commit version record**: Write to `spec_versions` table in SQLite.

### 6.3 Spec Validation Rules (12 rules)

| Code | Rule | Condition | Error Message |
|------|------|-----------|---------------|
| `MISSING_PURPOSE` | Purpose field is required | `purpose` is empty or missing | "Spec '{spec_id}' is missing a purpose. Every spec must describe what it accomplishes." |
| `AMBIGUOUS_REQUIREMENTS` | Requirements must be specific | Each requirement must contain an action verb and measurable outcome | "Requirement '{req}' in spec '{spec_id}' is ambiguous. Use format: 'System must [action] [object] [condition]'." |
| `UNDEFINED_DEPENDENCY` | Dependencies must exist | Each item in `dependencies[]` must be a known spec ID | "Spec '{spec_id}' depends on '{dep_id}', but no spec with that ID exists." |
| `MISSING_ACCEPTANCE_CRITERIA` | Acceptance criteria required | `acceptance_criteria` must have at least 1 item | "Spec '{spec_id}' is missing acceptance criteria. Every spec must define how to verify correct implementation." |
| `MISSING_TEST_CASES` | Test cases required | `test_cases` must have at least 1 item | "Spec '{spec_id}' is missing test cases. Every spec must define at least one test case." |
| `CONTRADICTS_EXISTING_SPEC` | No contradictions with active specs | LLM contradiction analysis score < 0.7 for all pairs | "Spec '{spec_id}' contradicts '{existing_id}' (score: {score}). Details: {description}" |
| `DEPENDENCY_CYCLE` | No circular dependencies | Topological sort of dependency graph must succeed | "Circular dependency detected: {cycle_path}. Remove or restructure dependencies to break the cycle." |
| `NARRATIVE_DRIFT` | Spec must align with constitution | Drift score >= 0.6 | "Spec '{spec_id}' has drifted from the project constitution (score: {score}). Consider revising to align with: '{constitution_excerpt}'" |
| `INCOMPLETE_SECURITY` | Security reqs for auth/data specs | If spec involves auth or PII, `security_requirements` must be non-empty | "Spec '{spec_id}' involves authentication/authorization or sensitive data but has no security requirements defined." |
| `DUPLICATE_ID` | Spec ID must be unique | `spec_id` must not exist in the active project | "A spec with ID '{spec_id}' already exists. Choose a different ID or use versioning." |
| `INVALID_STATUS_TRANSITION` | Status transitions must follow lifecycle | From→To must be a valid transition (Section 6.5) | "Cannot transition spec '{spec_id}' from '{current_status}' to '{target_status}'. Valid transitions: {valid_transitions}" |
| `MISSING_CONSTRAINTS` | Constraints field required | `constraints` must have at least 1 item | "Spec '{spec_id}' has no constraints. Every spec must define at least one hard constraint." |

### 6.4 Spec Lifecycle State Machine

```
                  ┌──────────┐
                  │  Draft   │
                  └────┬─────┘
                       │ validate
                       ▼
               ┌──────────────┐
               │  Validated   │
               └──────┬───────┘
                      │ approve
                      ▼
               ┌──────────────┐
               │  Approved    │
               └──────┬───────┘
                      │ activate
                      ▼
               ┌──────────────┐
               │   Active     │◀────────────┐
               └──────┬───────┘             │
                      │ implement           │ re-activate
                      ▼                     │
               ┌──────────────┐    ┌────────┴───────┐
               │ Implemented  │───▶│    Archived    │
               └──────┬───────┘    └────────────────┘
                      │ verify
                      ▼
               ┌──────────────┐
               │  Verified    │
               └──────┬───────┘
                      │ archive
                      ▼
               ┌──────────────┐
               │  Archived    │
               └──────────────┘
```

**Valid Transitions:**
- Draft → Validated (requires: validation rules pass)
- Validated → Approved (requires: manual review)
- Approved → Active (requires: dependencies resolved)
- Active → Implemented (requires: all tasks completed)
- Implemented → Verified (requires: acceptance criteria passed)
- Verified → Archived (requires: clean handoff)
- Active → Archived (direct: for specs that are no longer needed)
- Archived → Active (rollback: requires contradiction re-check)

**Rollback Rules:**
- A spec can be rolled back from any state to Draft via `sovereignspec spec compile --rollback`
- Rollback clears the `version` increment and restores previous DB record
- Archived → Active rollback requires contradiction re-check against all active specs

---

## 7. Layer 6 — Agent Integration Layer

### 7.1 Agent Adapter Interface (Abstract Base)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

class AgentAdapter(ABC):
    """Abstract base for all coding agent adapters."""

    @abstractmethod
    def load_specification(self, spec_id: str) -> "SpecificationContext":
        """Load a specification and return it in the agent's expected format."""
        pass

    @abstractmethod
    def load_context(self, spec_id: str) -> "AgentContextPackage":
        """Assemble and return the full context package for this agent."""
        pass

    @abstractmethod
    def generate_task(self, spec_id: str) -> "TaskList":
        """Generate task list in the agent's expected format."""
        pass

    @abstractmethod
    def submit_artifact(self, artifact_path: str, task_id: str) -> "ArtifactRecord":
        """Register an artifact submitted by the agent."""
        pass

    @abstractmethod
    def validate_output(self, artifact_id: str) -> "ValidationResult":
        """Validate that artifact output meets spec acceptance criteria."""
        pass
```

### 7.2 Context Assembly Engine

The agent context package (`agent_context.md`) is assembled from these sources:

| Section | Source | Selection Logic |
|---------|--------|----------------|
| Current Spec | `specs/{spec-id}.sspec` | Full spec content |
| Related Specs (5) | Knowledge graph | Top 5 by graph proximity (DEPENDS_ON, REFERENCES edges) |
| Relevant ADRs | Graph (Spec → REFERENCES → ADR) | All ADRs linked via REFERENCES from current or related specs |
| Repository Patterns | `patterns/pattern_library.json` | Top 10 patterns by relevance score to current spec |
| Graph Context | Knowledge graph | Dependency chain + what-breaks-if-changed for current spec |
| Active Tasks | `tasks/{spec-id}-tasks.md` | Current task list for this spec |
| Previous Artifacts | `agents/{agent-name}/artifacts.json` | Artifacts from previous sessions for this spec |

### 7.3 Supported Adapters

Each adapter writes integration files in the agent's expected format:

| Adapter | Files Written | Location |
|---------|--------------|----------|
| OpenCodeAdapter | `AGENTS.md` | Project root |
| ClaudeCodeAdapter | `CLAUDE.md` + `.claude/commands/*.md` | Project root |
| CodexAdapter | `AGENTS.md` + `skills/` | Project root |
| CursorAdapter | `.cursor/rules/*.mdc` | Project root |
| ClineAdapter | `.clinerules` | Project root |
| RooCodeAdapter | `.roo/rules.md` | Project root |
| WindsurfAdapter | `.windsurfrules` | Project root |
| ContinueAdapter | `.continue/config.json` + `.continue/commands/` | Project root |
| GeminiCLIAdapter | `GEMINI.md` | Project root |
| AiderAdapter | `.aider.conf.yml` | Project root |
| GenericFilesystemAdapter | `.sovereignspec/bootstrap.md` | `.sovereignspec/` (universal fallback) |

For full integration details per agent, see [docs/AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md).

### 7.4 Bootstrap Contract

The `.sovereignspec/bootstrap.md` file (see full content at [.sovereignspec/bootstrap.md](.sovereignspec/bootstrap.md)) is the universal contract that any file-aware coding agent reads to understand the SovereignSpec project.

It instructs any agent to:
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

---

## 8. Layer 7 — Interface Layer

### 8.1 Next.js App Router Structure

```
ui/
├── app/
│   ├── layout.tsx              (Root layout with sidebar navigation)
│   ├── page.tsx                (/ — Dashboard)
│   ├── projects/
│   │   └── [id]/
│   │       └── page.tsx        (/projects/[id] — Project View)
│   ├── specs/
│   │   ├── page.tsx            (/specs — Specification Browser)
│   │   ├── [id]/
│   │   │   └── page.tsx        (/specs/[id] — Spec Detail)
│   │   └── new/
│   │       └── page.tsx        (/specs/new — Spec Editor)
│   ├── graph/
│   │   └── page.tsx            (/graph — Knowledge Graph Explorer)
│   ├── tasks/
│   │   └── page.tsx            (/tasks — Task Board)
│   ├── docs/
│   │   └── page.tsx            (/docs — Documentation Hub)
│   └── settings/
│       └── page.tsx            (/settings — Configuration)
├── components/
│   ├── ui/                     (shadcn/ui components)
│   ├── spec-editor.tsx
│   ├── graph-visualization.tsx
│   ├── task-board.tsx
│   ├── project-card.tsx
│   └── agent-status.tsx
└── lib/
    ├── api.ts                  (API client)
    ├── types.ts                (TypeScript types)
    └── utils.ts
```

### 8.2 Screen Specifications

**Dashboard (`/`)**
- Route: `app/page.tsx`
- Components: `ProjectCard`, `RecentActivity`, `SpecHealthOverview`
- Data: Project list from SQLite `projects` table, recent sessions from `sessions`, spec status counts

**Project View (`/projects/[id]`)**
- Route: `app/projects/[id]/page.tsx`
- Components: `ProjectHeader`, `SpecList`, `AdrList`, `TaskSummary`, `AgentActivity`
- Data: Project details, specs, ADRs, tasks, agent sessions filtered by project_id

**Specification Browser (`/specs`)**
- Route: `app/specs/page.tsx`
- Components: `SpecFilters` (status dropdown), `SpecTable`, `SpecHealthBadge`
- Data: All specs from `specifications` table with status, version, drift score

**Spec Detail (`/specs/[id]`)**
- Route: `app/specs/[id]/page.tsx`
- Components: `SpecContent` (rendered .sspec), `GraphMini` (mini graph), `RelatedItems`, `VersionHistory`
- Data: Full spec, relationships from graph, versions from `spec_versions`, related ADRs

**Spec Editor (`/specs/new`)**
- Route: `app/specs/new/page.tsx`
- Components: `SpecForm` (YAML form with live validation), `FieldValidator`
- Data: POST to `/api/specs` on save

**Knowledge Graph Explorer (`/graph`)**
- Route: `app/graph/page.tsx`
- Components: `ForceDirectedGraph` (D3.js or vis-network), `GraphControls`, `NodeInspector`
- Data: Full graph from `graph.json`, filtered by node type

**Task Board (`/tasks`)**
- Route: `app/tasks/page.tsx`
- Components: `KanbanBoard`, `TaskCard`, `TaskFilters`
- Data: Tasks from `tasks` table grouped by status (pending/in_progress/completed)

**Documentation Hub (`/docs`)**
- Route: `app/docs/page.tsx`
- Components: `DocTree` (file browser), `DocViewer` (markdown renderer)
- Data: Generated docs from `.sovereignspec/docs/`

**Settings (`/settings`)**
- Route: `app/settings/page.tsx`
- Components: `ModelConfig`, `AdapterConfig`, `ChromaConfig`, `PathConfig`
- Data: Read/write `config.json`

### 8.3 shadcn/ui Component Mapping

| Screen | shadcn/ui Components |
|--------|---------------------|
| Dashboard | Card, Badge, ScrollArea |
| Project View | Tabs, Table, Card, Badge |
| Spec Browser | Table, Select, Badge, Input |
| Spec Detail | Tabs, Card, Separator, ScrollArea |
| Spec Editor | Form, Textarea, Input, Button, Alert |
| Graph Explorer | Dialog, Sheet, Tooltip |
| Task Board | Card, Badge, Select, Button |
| Doc Hub | Tree, ScrollArea |
| Settings | Form, Input, Select, Switch, Button |

### 8.4 API Routes

**`GET /api/projects`** — List all projects
```json
{ "projects": [{ "id": "uuid", "name": "...", "spec_count": 5, "health": "good" }] }
```

**`GET /api/projects/:id`** — Project details
```json
{ "id": "uuid", "name": "...", "specs": [...], "adrs": [...], "tasks": [...] }
```

**`GET /api/specs`** — List specs with optional `?status=active` filter
```json
{ "specs": [{ "id": "spec-jwt-auth", "title": "...", "status": "active", "version": "1.0.0" }] }
```

**`GET /api/specs/:id`** — Full spec with graph context
```json
{ "spec": { "id": "...", "content": {...}, "relationships": [...], "versions": [...] } }
```

**`POST /api/specs`** — Create new spec
```json
{ "spec_id": "...", "title": "...", "content": "..." }
```

**`GET /api/graph`** — Full knowledge graph
```json
{ "nodes": [...], "edges": [...] }
```

**`GET /api/graph/query?what_breaks=spec-id`** — Graph query
```json
{ "affected_nodes": [...], "dependency_chain": {...} }
```

**`GET /api/tasks`** — Task list
```json
{ "tasks": [{ "id": "...", "title": "...", "status": "pending" }] }
```

**`PUT /api/tasks/:id`** — Update task status
```json
{ "status": "completed" }
```

**`GET /api/docs`** — Documentation tree
```json
{ "files": [{ "path": "docs/jwt-auth/implementation.md", "type": "file" }] }
```

**`GET /api/settings`** — Current configuration
```json
{ "model": "qwen2.5-coder:32b", "adapter": "claude-code", "chroma_path": "..." }
```

**`PUT /api/settings`** — Update configuration
```json
{ "model": "llama3.1:70b" }
```

**`GET /api/health`** — System health
```json
{ "ollama": true, "chroma": true, "sqlite": true, "models": ["qwen2.5-coder:32b"] }
```

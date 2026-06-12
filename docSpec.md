# SOVEREIGNSPEC — COMPLETE DOCUMENTATION GENERATION PROMPT
# Agent: You are a senior software architect and technical documentation engineer.
# Mission: Generate ALL documentation artifacts required to fully construct SovereignSpec
#          from scratch. Output every file listed below with complete, production-ready content.
#          Do not summarize. Do not truncate. Generate each document fully.

---

## PROJECT IDENTITY

Name: SovereignSpec
Tagline: Local-First Specification Operating System for AI Development
Repository: https://github.com/kliewerdaniel/sovereignSpec
Author: Daniel Kliewer (danielkliewer.com)
Version Target: 1.0.0
License: MIT

Core thesis:
  Human → Specification → SovereignSpec → Agent → Implementation
  The specification is the durable artifact. The code is disposable.
  The spec is alive. The code obeys. Nothing leaves your machine.

---

## DOCUMENTATION ARTIFACTS TO GENERATE

Generate every file listed below as a complete, standalone document.
Each file must be fully written — no placeholders, no "TBD", no stubs.

---

### FILE 1: README.md

Generate a comprehensive root README.md containing:

1. Project banner and tagline
2. Badges: version, license, build status, stars
3. Executive Summary (3–4 paragraphs):
   - SovereignSpec is a local-first, fully offline Spec-Driven Development (SDD) engine
   - Treats specifications as living, graph-grounded knowledge artifacts, not flat markdown
   - Enforces deterministic code generation via GBNF grammar constraints
   - Tracks spec drift, semantic contradictions, and narrative evolution across versions
   - Zero cloud API calls required — all inference via Ollama (llama-cpp compatible)
   - Agent-agnostic: integrates with OpenCode, Claude Code, Cursor, Cline, RooCode,
     Codex, Gemini CLI, Aider, Windsurf, Continue, and any file-aware coding agent
     without custom plugins, solely through the filesystem and specification files

4. Why SovereignSpec exists (contrast with GitHub Spec Kit):
   - Spec Kit (github/spec-kit, 108K+ stars) proved SDD works but requires cloud APIs at
     every pipeline step (/clarify, /plan, /implement all call external LLM endpoints)
   - Spec Kit has no RAG integration — specs are flat markdown, ungrounded in knowledge
   - Spec Kit has no GBNF grammar enforcement — generated code is unconstrained
   - Spec Kit has no semantic spec diffing, contradiction detection, or narrative drift tracking
   - SovereignSpec fills the local-first SDD gap: same workflow, zero cloud dependency

5. Architecture overview diagram (ASCII):

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

6. Tech stack table:
   Component          | Technology
   ─────────────────────────────────────
   UI Framework       | Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui
   Local LLM          | Ollama (Qwen, Llama 3.1, DeepSeek, Gemma, Mistral)
   Vector Store       | ChromaDB (local, embedded)
   Metadata DB        | SQLite (via better-sqlite3 or Drizzle ORM)
   Graph Store        | NetworkX (Python) / adjacency JSON (default), Neo4j (optional)
   CLI                | Python 3.11+ with Click or Typer
   Grammar Enforcement| GBNF (llama-cpp grammar files)
   Spec Format        | .sspec (YAML-superset)
   Package Manager    | uv (Python) + pnpm (Node)

7. Quick start (5 steps):
   a. Install: uv tool install sovereignspec
   b. Initialize: sovereignspec init my-project
   c. Run agent in project dir, commands are available as /sovereign.*
   d. /sovereign.constitution — establish project principles
   e. /sovereign.specify — define what to build
   f. /sovereign.clarify → /sovereign.plan → /sovereign.tasks → /sovereign.implement

8. CLI command reference table (all 8 commands with descriptions)
9. Spec file format (.sspec) example
10. Agent bootstrap pattern explanation (.sovereignspec/bootstrap.md)
11. Directory structure tree after `sovereignspec init`
12. Contributing section
13. License

---

### FILE 2: ARCHITECTURE.md

Generate a complete architecture document containing:

1. System overview and design philosophy:
   - Five core principles (Local First, Agent Agnostic, Specification As Source,
     Sovereign Memory, Deterministic Development) — each with 2–3 paragraphs of rationale
   - Contrast with vibe coding: hallucination rate comparison, rework cycles, scalability
   - Contrast with Spec Kit: cloud dependency problem, RAG gap, grammar enforcement gap,
     spec evolution tracking gap

2. Layer 1 — Local Infrastructure:
   Full specification of:
   - Ollama integration: model loading, inference API calls, streaming, model selection config
   - ChromaDB: collection design, embedding strategy, distance metrics, persistence path
   - SQLite schema (all tables with full column definitions, types, constraints, indexes):
     * projects (id, name, slug, constitution_path, created_at, updated_at, status)
     * specifications (id, project_id, spec_id, title, status, file_path, version,
                       created_at, updated_at, checksum, parent_id)
     * spec_relationships (id, source_spec_id, target_spec_id, relationship_type,
                           created_at, metadata_json)
     * spec_versions (id, spec_id, version, content_hash, diff_summary, created_at,
                      contradictions_json, drift_score)
     * adrs (id, project_id, number, title, status, file_path, created_at)
     * tasks (id, spec_id, title, status, agent_id, created_at, completed_at, output_path)
     * agents (id, name, adapter_type, last_seen, capabilities_json)
     * artifacts (id, task_id, artifact_type, file_path, validated, created_at)
     * patterns (id, project_id, pattern_type, name, example, created_at)
     * sessions (id, project_id, agent_id, started_at, ended_at, context_hash)
   - File watcher design: chokidar (Node) or watchdog (Python), event debounce, triggers

3. Layer 2 — Persistence Layer:
   - Specification storage protocol: .sspec file format, versioning strategy,
     checksum computation (SHA-256), diff generation
   - ADR storage: /docs/adr/ADR-NNN.md naming convention, linking to specs
   - Task storage: tasks.json + tasks.md dual-write for agent compatibility
   - Artifact registry: tracking all agent-generated outputs with validation status

4. Layer 3 — Repository Intelligence:
   - Repository mapping algorithm: walk directory tree, identify languages via extension,
     find entrypoints (main.*, index.*, app.*), detect framework conventions
   - repository_map.json schema (full JSON schema definition)
   - Pattern extraction: AST-based (tree-sitter) or heuristic fallback for:
     * naming conventions, error handling patterns, test file patterns,
       import organization, API route conventions
   - pattern_library.json schema
   - Semantic search: ChromaDB query pipeline for repository knowledge retrieval
   - Example queries and expected retrieval behavior

5. Layer 4 — Knowledge Graph:
   - Node types (11 types): Project, Feature, Specification, Module, Service,
     Endpoint, Database, ADR, Task, Agent, Document
   - Relationship types (9 types): IMPLEMENTS, DEPENDS_ON, REFERENCES, GENERATES,
     REPLACES, SUPERSEDES, CONFLICTS_WITH, RELATED_TO, VALIDATES
   - Graph storage: adjacency list JSON format (default, zero dependencies):
     {
       "nodes": [{"id": "string", "type": "NodeType", "metadata": {}}],
       "edges": [{"source": "string", "target": "string", "type": "RelType", "weight": 1.0}]
     }
   - Neo4j optional upgrade path: Cypher query equivalents for all graph operations
   - NetworkX Python bridge: loading adjacency JSON, executing graph queries
   - Graph query API: what_breaks_if_changed(spec_id), what_specs_affect_module(module_id),
     which_adr_created_architecture(pattern_name), dependency_chain(spec_id)
   - Spec contradiction detection algorithm:
     * Embed spec content via Ollama embeddings
     * Cluster related specs via ChromaDB similarity
     * Prompt local LLM with GBNF-constrained output to score contradiction likelihood
     * Store contradiction pairs in spec_relationships table
   - Narrative drift tracking algorithm:
     * Extract project constitution vector at initialization
     * Compute cosine similarity of each new spec against constitution vector
     * Flag specs with drift_score < 0.6 for review
     * Store drift history in spec_versions table

6. Layer 5 — Specification Engine:
   - .sspec file format complete specification:
     YAML superset with required and optional fields:
     Required: id, title, version, status, purpose, requirements[], constraints[],
               acceptance_criteria[], dependencies[], test_cases[]
     Optional: security_requirements[], performance_requirements[], architecture_notes,
               non_functional_requirements[], related_adrs[], implementation_hints
   - Full annotated example .sspec file (JWT authentication spec)
   - Spec compiler pipeline:
     1. Parse .sspec YAML
     2. Validate required fields (raise SpecValidationError on failure)
     3. Resolve dependency graph (topological sort)
     4. Check for contradictions against existing specs in ChromaDB
     5. Compute drift score against constitution
     6. Generate implementation plan (Markdown)
     7. Generate task tree (tasks.md)
     8. Generate agent context package (agent_context.md)
     9. Generate documentation bundle (/docs/**)
     10. Update knowledge graph (nodes + edges)
     11. Update ChromaDB embeddings
     12. Commit spec version record to SQLite
   - Spec validation rules (12 rules with error messages):
     * MISSING_PURPOSE, AMBIGUOUS_REQUIREMENTS, UNDEFINED_DEPENDENCY,
       MISSING_ACCEPTANCE_CRITERIA, MISSING_TEST_CASES, CONTRADICTS_EXISTING_SPEC,
       DEPENDENCY_CYCLE, NARRATIVE_DRIFT, INCOMPLETE_SECURITY, DUPLICATE_ID,
       INVALID_STATUS_TRANSITION, MISSING_CONSTRAINTS
   - Spec lifecycle state machine:
     Draft → Validated → Approved → Active → Implemented → Verified → Archived
     With allowed transitions, validation gates per transition, and rollback rules

7. Layer 6 — Agent Integration Layer:
   - Agent Adapter interface (abstract base):
     load_specification(spec_id) → SpecificationContext
     load_context(spec_id) → AgentContextPackage
     generate_task(spec_id) → TaskList
     submit_artifact(artifact_path, task_id) → ArtifactRecord
     validate_output(artifact_id) → ValidationResult
   - Context Assembly Engine:
     Builds agent_context.md by assembling:
     * Current spec content (full)
     * Related specs (top 5 by graph proximity)
     * Relevant ADRs (linked via spec graph)
     * Repository patterns (top 10 by relevance)
     * Graph context (dependency chain, what-breaks-if-changed)
     * Active tasks (from tasks.md)
     * Previous implementation artifacts (if any)
   - Supported adapters and their bootstrap file conventions:
     * OpenCodeAdapter: writes to AGENTS.md
     * ClaudeCodeAdapter: writes to CLAUDE.md + .claude/commands/
     * CodexAdapter: writes to AGENTS.md + codex-skills
     * CursorAdapter: writes to .cursor/rules/
     * ClineAdapter: writes to .clinerules
     * RooCodeAdapter: writes to .roo/rules.md
     * WindsurfAdapter: writes to .windsurfrules
     * ContinueAdapter: writes to .continue/config.json
     * GenericFilesystemAdapter: writes to .sovereignspec/bootstrap.md (universal fallback)
   - bootstrap.md format specification (the universal contract):
     The bootstrap.md instructs any file-aware agent to:
     1. Read .sovereignspec/specs/ for active specifications
     2. Read .sovereignspec/adr/ for architectural decisions
     3. Read .sovereignspec/patterns/pattern_library.json for coding conventions
     4. Read .sovereignspec/tasks/active_tasks.md for current work units
     5. Honor all constraints listed in active specs
     6. Update implementation status upon task completion
     7. Generate tests for every implemented feature
     8. Generate documentation for every module changed
     9. Update .sovereignspec/graph/graph.json with new relationships
     10. Record all decisions as new ADR drafts in .sovereignspec/adr/

8. Layer 7 — Interface Layer:
   - Next.js App Router structure
   - All 9 major screens with route paths, components, and data requirements:
     * / (Dashboard): project list, recent activity, spec health overview
     * /projects/[id] (Project View): specs, ADRs, tasks, agent activity
     * /specs (Specification Browser): all specs with lifecycle status filters
     * /specs/[id] (Spec Detail): full spec, graph visualization, related items
     * /specs/new (Spec Editor): .sspec form editor with live validation
     * /graph (Knowledge Graph Explorer): interactive force-directed graph
     * /tasks (Task Board): kanban-style task tracking by spec
     * /docs (Documentation Hub): auto-generated docs browser
     * /settings (Settings): Ollama model config, agent adapter config, ChromaDB path
   - shadcn/ui component mapping per screen
   - API routes (/api/**) with request/response schemas

---

### FILE 3: docs/INSTALLATION.md

Generate complete installation documentation:

1. Prerequisites checklist:
   - Python 3.11+, uv, Node.js 18+, pnpm, Git
   - Ollama (https://ollama.ai) — installation commands for macOS, Linux, Windows
   - Recommended Ollama models with pull commands:
     * ollama pull llama3.1:70b (best quality, high RAM)
     * ollama pull qwen2.5-coder:32b (best for code generation)
     * ollama pull deepseek-coder-v2:16b (balanced)
     * ollama pull mistral:7b (minimum spec)
   - ChromaDB: pip install chromadb (auto-installed via uv)
   - SQLite: bundled with Python

2. Installation methods:
   a. Via uv (recommended):
      uv tool install sovereignspec --from git+https://github.com/kliewerdaniel/sovereignSpec.git
   b. Development install:
      git clone https://github.com/kliewerdaniel/sovereignSpec.git
      cd sovereignSpec
      uv sync
      uv run sovereignspec --help
   c. Verify installation:
      sovereignspec --version
      sovereignspec doctor  (checks Ollama, ChromaDB, SQLite connectivity)

3. Project initialization:
   sovereignspec init my-project
   sovereignspec init .  (current directory)
   sovereignspec init . --force  (non-empty directory)
   sovereignspec init . --model qwen2.5-coder:32b  (specify Ollama model)
   sovereignspec init . --integration claude-code  (pre-configure agent adapter)

4. Directory structure created by init:
   .sovereignspec/
   ├── config.json           (project config: model, adapters, paths)
   ├── bootstrap.md          (universal agent bootstrap — the contract)
   ├── constitution.md       (project governing principles)
   ├── specs/                (all .sspec files)
   ├── adr/                  (ADR-NNN.md files)
   ├── tasks/                (task lists per spec)
   ├── patterns/             (pattern_library.json, repository_map.json)
   ├── memory/               (persistent agent memory blobs)
   ├── graph/                (graph.json — knowledge graph adjacency list)
   ├── agents/               (agent session records)
   ├── grammar/              (GBNF grammar files per output type)
   └── docs/                 (auto-generated documentation)

5. Integrating with each supported agent (one section per agent):
   - Claude Code: sovereignspec integrate --agent claude-code
   - OpenCode: sovereignspec integrate --agent opencode
   - Cursor: sovereignspec integrate --agent cursor
   - Cline: sovereignspec integrate --agent cline
   - Codex: sovereignspec integrate --agent codex
   - Continue: sovereignspec integrate --agent continue
   - Windsurf: sovereignspec integrate --agent windsurf
   - Generic: sovereignspec integrate --agent generic
   Each section must explain what files are written and what the agent will see.

6. Configuration reference (config.json schema with all fields and defaults)

7. Troubleshooting: 10 common issues with diagnosis and resolution steps

---

### FILE 4: docs/SPECIFICATION_FORMAT.md

Generate a complete specification format reference:

1. Philosophy: why .sspec instead of plain markdown
   - Structured fields enable programmatic validation
   - Machine-readable = compiler-processable = deterministic output
   - Evolution tracking requires stable field identity
   - Graph integration requires typed relationships
   - GBNF grammar requires typed output schemas

2. Complete .sspec field reference:

   Every field documented with:
   - Field name, type, required/optional
   - Description and purpose
   - Valid values or format
   - Example value
   - Validation rules
   - Effect on compilation

   Fields:
   id (string, required): kebab-case unique identifier, immutable after first commit
   title (string, required): human-readable spec title
   version (semver string, required): spec version, e.g. "1.0.0"
   status (enum, required): draft|validated|approved|active|implemented|verified|archived
   purpose (string, required): 1–3 sentence description of what this spec accomplishes
   requirements (list[string], required): functional requirements, minimum 1
   constraints (list[string], required): hard limits (security, performance, architecture)
   acceptance_criteria (list[string], required): testable pass/fail criteria
   dependencies (list[string], required): list of spec IDs this spec depends on (can be [])
   test_cases (list[object], required): structured test cases
     test_cases[].id: unique test ID
     test_cases[].description: what is being tested
     test_cases[].given: preconditions
     test_cases[].when: action taken
     test_cases[].then: expected outcome
   security_requirements (list[string], optional): security-specific requirements
   performance_requirements (list[object], optional):
     performance_requirements[].metric: e.g. "p95 response time"
     performance_requirements[].threshold: e.g. "< 200ms"
   architecture_notes (string, optional): free-form architectural guidance
   non_functional_requirements (list[string], optional): NFRs
   related_adrs (list[string], optional): ADR IDs, e.g. ["ADR-004"]
   implementation_hints (list[string], optional): hints for the coding agent
   tags (list[string], optional): categorization tags

3. Full annotated example — JWT Authentication specification:
   (Write a complete, realistic .sspec for JWT auth with all required and relevant
    optional fields fully populated)

4. Full annotated example — User Profile API specification:
   (Write a complete, realistic .sspec for a user profile CRUD API)

5. Full annotated example — Database Migration specification:
   (Write a complete, realistic .sspec for a database migration workflow)

6. Spec relationship types explained with examples:
   - DEPENDS_ON: spec A must be implemented before spec B
   - IMPLEMENTS: spec A is the implementation target for feature B
   - REFERENCES: spec A refers to spec B for shared context
   - SUPERSEDES: spec A replaces spec B (B moves to archived)
   - CONFLICTS_WITH: spec A and spec B have contradictory requirements

7. Spec validation error reference (all 12 error codes with examples and remediation)

8. Spec compiler output documentation:
   For each .sspec, the compiler generates:
   - docs/[spec-id]/implementation.md
   - docs/[spec-id]/testing.md
   - docs/[spec-id]/api.md (if applicable)
   - docs/[spec-id]/deployment.md
   - tasks/[spec-id]-tasks.md
   - agent_context/[spec-id]-context.md

---

### FILE 5: docs/CLI_REFERENCE.md

Generate a complete CLI command reference:

For each command, document: usage, description, options, arguments, examples, output.

Commands:

sovereignspec init [path] [options]
sovereignspec doctor
sovereignspec integrate --agent <adapter>
sovereignspec spec create [spec-id] [--title "..."]
sovereignspec spec validate [spec-id|--all]
sovereignspec spec compile [spec-id|--all]
sovereignspec spec list [--status <status>]
sovereignspec spec diff [spec-id] [--version v1] [--version v2]
sovereignspec spec graph [spec-id]
sovereignspec sovereign-constitution [description]
sovereignspec specify [description]
sovereignspec clarify [spec-id]
sovereignspec plan [spec-id] [--tech-stack "..."]
sovereignspec tasks [spec-id]
sovereignspec analyze [spec-id|--all]
sovereignspec implement [spec-id]
sovereignspec adr create [--title "..."] [--context "..."]
sovereignspec adr list
sovereignspec context build [spec-id] [--agent <adapter>]
sovereignspec graph query [--what-breaks spec-id] [--affects-module module-name]
sovereignspec memory sync
sovereignspec memory status
sovereignspec repo map
sovereignspec repo patterns
sovereignspec agent list
sovereignspec agent status [agent-name]
sovereignspec docs generate [spec-id|--all]

Also document:
- Global flags: --project-dir, --model, --verbose, --json (machine-readable output)
- Environment variables: SOVEREIGNSPEC_MODEL, SOVEREIGNSPEC_OLLAMA_HOST,
  SOVEREIGNSPEC_DB_PATH, SOVEREIGNSPEC_CHROMA_PATH
- Exit codes: 0 success, 1 validation error, 2 compilation error, 3 graph error,
  4 agent error, 5 LLM unavailable

---

### FILE 6: docs/AGENT_INTEGRATION.md

Generate a complete agent integration guide:

1. The Agent Contract:
   Every agent integrated with SovereignSpec must:
   - Read specifications before writing any code
   - Update implementation status in tasks/[spec-id]-tasks.md upon task completion
   - Generate tests for every implemented feature
   - Generate documentation for every module changed
   - Update .sovereignspec/graph/graph.json with new relationship edges
   - Record all architectural decisions as ADR drafts
   - Submit artifact paths to .sovereignspec/agents/[agent-name]/artifacts.json

2. The bootstrap.md universal contract (full content):
   Write the exact content that would appear in .sovereignspec/bootstrap.md.
   This is the single file that any file-aware coding agent can read to understand
   the SovereignSpec contract. It must be self-contained and unambiguous.

3. Per-agent integration documentation (one complete section per agent):

   For each agent, document:
   a. What files SovereignSpec writes for this agent
   b. The exact content of each written file
   c. How the agent discovers SovereignSpec commands
   d. How the agent should respond to each /sovereign.* command
   e. How the agent submits completed artifacts back

   Agents to document:
   - Claude Code (CLAUDE.md + .claude/commands/*.md)
   - OpenCode (AGENTS.md)
   - Cursor (.cursor/rules/*.mdc)
   - Cline (.clinerules)
   - RooCode (.roo/rules.md)
   - Codex CLI (AGENTS.md + skills mode)
   - Gemini CLI (GEMINI.md)
   - Aider (.aider.conf.yml + system prompt injection)
   - Windsurf (.windsurfrules)
   - Continue (.continue/config.json)
   - Generic filesystem agent (.sovereignspec/bootstrap.md fallback)

4. The /sovereign.* slash command specifications:

   For each command, write the complete prompt template that SovereignSpec installs
   into the agent's command directory. This is what the agent reads when a user runs
   the command. Each template must be self-contained and instruct the agent precisely.

   Commands with full prompt templates:
   /sovereign.constitution  — Create or update governing principles
   /sovereign.specify       — Define a new feature/system to build
   /sovereign.clarify       — RAG-grounded clarification of a spec
   /sovereign.plan          — Generate technical implementation plan
   /sovereign.tasks         — Decompose plan into actionable task list
   /sovereign.analyze       — Cross-spec consistency + contradiction analysis
   /sovereign.implement     — Execute tasks against spec constraints
   /sovereign.checklist     — Generate spec quality checklist

5. Context package format (agent_context.md):
   Document the exact structure of the context package assembled for each agent,
   including all sections, their sources, and assembly logic.

6. Artifact submission protocol:
   Document the exact JSON format agents use to register completed artifacts:
   Path: .sovereignspec/agents/[agent-name]/artifacts.json
   Schema with all fields, types, and valid values.

---

### FILE 7: docs/KNOWLEDGE_GRAPH.md

Generate complete knowledge graph documentation:

1. Graph philosophy: why specs must be nodes, not documents
2. Node type specifications (all 11 types with fields and creation rules)
3. Edge type specifications (all 9 types with directionality and weight semantics)
4. graph.json format specification (complete JSON schema)
5. Graph operations API:
   - add_node(id, type, metadata) → node_id
   - add_edge(source_id, target_id, type, weight, metadata) → edge_id
   - what_breaks_if_changed(spec_id) → list[Node]
   - what_specs_affect_module(module_path) → list[Specification]
   - which_adr_created_architecture(pattern) → list[ADR]
   - dependency_chain(spec_id, depth) → Tree
   - find_contradictions() → list[ContradictionPair]
   - compute_drift_score(spec_id) → float
6. Contradiction detection algorithm (full pseudocode + prose explanation)
7. Narrative drift tracking algorithm (full pseudocode + prose explanation)
8. Neo4j upgrade guide: Cypher equivalents for all graph operations
9. Graph query examples with expected outputs

---

### FILE 8: docs/GBNF_GRAMMARS.md

Generate complete GBNF grammar documentation:

1. Why GBNF matters for sovereign development:
   - Local LLMs without grammar constraints hallucinate syntax
   - GBNF constrains the output token probability space to valid structures
   - Deterministic output = reproducible implementations
   - Grammar-constrained output is parseable without error handling

2. Grammar files included with SovereignSpec:
   For each grammar file, document: purpose, file path, full grammar content, example output

   Grammar files:
   a. grammar/spec_validation_result.gbnf — LLM contradiction scoring output
   b. grammar/implementation_plan.gbnf — structured implementation plan
   c. grammar/task_list.gbnf — structured task list with dependencies
   d. grammar/api_spec.gbnf — OpenAPI-compatible endpoint spec
   e. grammar/adr.gbnf — Architecture Decision Record
   f. grammar/test_case.gbnf — structured test case output
   g. grammar/contradiction_report.gbnf — spec contradiction analysis
   h. grammar/drift_report.gbnf — narrative drift analysis

3. How grammars integrate with Ollama:
   Complete code example showing how to pass GBNF grammar to Ollama API
   in both streaming and non-streaming modes.

4. Writing custom grammars: tutorial with 3 examples of progressively complex grammars

---

### FILE 9: docs/SPEC_DRIVEN_WORKFLOW.md

Generate a complete workflow guide for SovereignSpec users:

1. SDD concepts (for users new to Spec-Driven Development):
   - The context hierarchy (5 layers from global rules to task context)
   - Functional specs vs technical specs: the separation principle
   - Specs as upstream artifacts: code is downstream, disposable, regenerable
   - The SDD artifact stack: what documents you need and why

2. Complete walkthrough — building a REST API from zero to implementation:
   Phase 1: Initialize project and establish constitution
   Phase 2: Write the first specification (/sovereign.specify)
   Phase 3: Clarify the spec (/sovereign.clarify)
   Phase 4: Generate implementation plan (/sovereign.plan)
   Phase 5: Break into tasks (/sovereign.tasks)
   Phase 6: Analyze for consistency (/sovereign.analyze)
   Phase 7: Implement (/sovereign.implement)
   Phase 8: Verify implementation against acceptance criteria
   Phase 9: Archive spec and update knowledge graph

3. Working with multiple specs: dependency management, ordering, parallel specs
4. Spec evolution: how to update a spec without losing history
5. Contradiction resolution workflow: what to do when analyze flags a contradiction
6. Narrative drift remediation: how to detect and fix scope creep at the spec level
7. ADR workflow: when to create ADRs, how they link to specs
8. Multi-agent workflow: using SovereignSpec with multiple agents simultaneously
9. Common patterns: authentication, CRUD APIs, event systems, background jobs
10. Anti-patterns to avoid (with examples of each)

---

### FILE 10: docs/adr/ADR-001.md

Generate the first ADR — Local-First Architecture Decision:

Sections: Title, Status (Accepted), Date, Context, Decision, Rationale, Alternatives Considered,
Consequences (positive and negative), Related Specs, Related ADRs

Topic: Why SovereignSpec requires zero cloud API calls and all inference runs locally

---

### FILE 11: docs/adr/ADR-002.md

Generate ADR — Specification Graph Node Model:

Topic: Why specifications are graph nodes (not flat markdown files) and what this enables

---

### FILE 12: docs/adr/ADR-003.md

Generate ADR — GBNF Grammar Enforcement:

Topic: Why GBNF grammars are used to constrain LLM output during code generation

---

### FILE 13: docs/adr/ADR-004.md

Generate ADR — ChromaDB for Vector Storage:

Topic: Why ChromaDB was chosen over alternatives (Qdrant, Pinecone, Weaviate, FAISS)
and the trade-offs of the local-embedded approach

---

### FILE 14: docs/adr/ADR-005.md

Generate ADR — Agent Agnostic Bootstrap Protocol:

Topic: Why SovereignSpec communicates with agents via filesystem files only (never APIs)
and the design of the bootstrap.md universal contract

---

### FILE 15: docs/adr/ADR-006.md

Generate ADR — SQLite as Primary Metadata Store:

Topic: Why SQLite (not PostgreSQL, MongoDB, or DuckDB) is the right choice for
local-first persistent metadata, including concurrency considerations

---

### FILE 16: .sovereignspec/bootstrap.md (TEMPLATE)

Generate the universal bootstrap.md file that is installed in every project by
`sovereignspec init`. This file is the primary interface between SovereignSpec
and any file-aware coding agent.

This file must be completely self-contained and cover:
1. What SovereignSpec is (one paragraph)
2. Your role as a coding agent using this project
3. Required reading before any implementation (ordered list of files to read)
4. The agent contract (what you must do for every task)
5. Specification format reference (quick reference for .sspec fields)
6. How to read active tasks (tasks.md format)
7. How to submit completed work (artifacts.json format)
8. How to create ADR drafts (ADR format)
9. Constraints you must never violate
10. How to update the knowledge graph after implementation

---

### FILE 17: .sovereignspec/templates/spec-template.sspec

Generate the default .sspec template file installed by sovereignspec init.
Include all fields with inline comments explaining each field's purpose
and valid values. Use YAML comment syntax (#).

---

### FILE 18: .sovereignspec/templates/adr-template.md

Generate the ADR template installed by sovereignspec init.
Include all sections with instructions for each section.

---

### FILE 19: .sovereignspec/templates/tasks-template.md

Generate the tasks.md template that the compiler produces for each spec.
Include: task header, per-user-story sections, dependency notation [P] for parallel,
checkpoint validation markers, file path specifications, test task ordering.

---

### FILE 20: docs/DEVELOPMENT.md

Generate a complete development guide for contributors:

1. Development environment setup (full step-by-step)
2. Project structure explanation (every directory and its purpose)
3. Python package structure:
   sovereignspec/
   ├── __init__.py
   ├── cli/
   │   ├── __init__.py
   │   ├── main.py           (Click/Typer root)
   │   ├── commands/
   │   │   ├── init.py
   │   │   ├── spec.py
   │   │   ├── sovereign.py  (the /sovereign.* workflow commands)
   │   │   ├── graph.py
   │   │   ├── context.py
   │   │   ├── adr.py
   │   │   ├── memory.py
   │   │   ├── repo.py
   │   │   └── docs.py
   ├── engine/
   │   ├── __init__.py
   │   ├── compiler.py       (spec compiler pipeline)
   │   ├── validator.py      (spec validation rules)
   │   ├── graph.py          (knowledge graph operations)
   │   ├── rag.py            (ChromaDB RAG pipeline)
   │   ├── grammar.py        (GBNF grammar loading + Ollama integration)
   │   ├── contradiction.py  (contradiction detection algorithm)
   │   ├── drift.py          (narrative drift tracking)
   │   └── repository.py     (repo mapping + pattern extraction)
   ├── adapters/
   │   ├── __init__.py
   │   ├── base.py           (AgentAdapter abstract base)
   │   ├── claude_code.py
   │   ├── opencode.py
   │   ├── cursor.py
   │   ├── cline.py
   │   ├── roocode.py
   │   ├── codex.py
   │   ├── gemini_cli.py
   │   ├── aider.py
   │   ├── windsurf.py
   │   ├── continue_.py
   │   └── generic.py
   ├── persistence/
   │   ├── __init__.py
   │   ├── db.py             (SQLite operations)
   │   ├── chroma.py         (ChromaDB operations)
   │   └── migrations/       (SQLite migration files)
   ├── models/
   │   ├── __init__.py
   │   ├── spec.py           (Pydantic models for .sspec)
   │   ├── graph.py          (Pydantic models for graph)
   │   ├── task.py
   │   ├── adr.py
   │   └── artifact.py
   └── ui/                   (Next.js app — separate from Python package)
       ├── app/
       ├── components/
       └── lib/

4. Testing strategy: unit tests, integration tests, LLM-in-the-loop tests
5. How to add a new agent adapter (step-by-step with code examples)
6. How to add a new GBNF grammar
7. How to add a new spec validation rule
8. Contribution workflow (branch naming, commit conventions, PR process)
9. Release process

---

### FILE 21: docs/SECURITY.md

Generate a complete security documentation file:

1. Security model: local-first means no network attack surface for inference
2. Prompt injection defenses:
   - GBNF grammar constraints as primary defense
   - Input sanitization for all spec fields
   - Spec field length limits
   - No execution of spec content as code
3. Spec file integrity:
   - SHA-256 checksums for all .sspec files
   - Tamper detection on spec versions
4. Agent output validation:
   - All agent artifacts validated against spec acceptance criteria
   - Validation output stored with audit trail
5. Dependency security:
   - Supply chain considerations for Ollama models
   - ChromaDB data isolation
   - SQLite file permissions
6. Air-gap operation security considerations

---

### FILE 22: CONTRIBUTING.md

Generate a complete contribution guide including:
1. Code of conduct summary
2. How to report bugs
3. How to request features
4. Development setup
5. Pull request process
6. Coding standards (Python: ruff, mypy; TypeScript: eslint, prettier)
7. Commit message conventions (Conventional Commits)
8. Testing requirements (coverage thresholds)
9. Documentation requirements for PRs

---

## GENERATION INSTRUCTIONS

1. Generate every file completely. Do not omit sections.
2. All code examples must be syntactically correct and runnable.
3. All schemas must be complete with every field documented.
4. All .sspec examples must be valid according to the spec format defined in FILE 4.
5. All ADRs must follow the template defined in FILE 18.
6. The bootstrap.md (FILE 16) must be a complete, deployable file — not a template description.
7. Maintain consistency: all spec IDs, command names, field names, and path conventions
   must be identical across all documents.
8. Every document must reference the principle that this is a LOCAL-FIRST system —
   no cloud API calls, no external dependencies for inference.
9. The agent integration documents must make it possible for someone using ANY of the
   listed coding agents to integrate SovereignSpec without any additional instructions.
10. This documentation set, when followed by a coding agent, must be sufficient to
    construct SovereignSpec from scratch with no further clarification required.

---

## COHERENCE REQUIREMENTS

The following terms must be used consistently across all documents:

- The spec file extension is always: .sspec
- The CLI binary name is always: sovereignspec
- The project directory is always: .sovereignspec/
- The knowledge graph file is always: .sovereignspec/graph/graph.json
- The bootstrap file is always: .sovereignspec/bootstrap.md
- The constitution file is always: .sovereignspec/constitution.md
- Slash commands are always prefixed: /sovereign.
  (not /speckit., not /sovereignspec., not /ss.)
- The graph storage default is always: adjacency JSON (not Neo4j)
- The vector store is always: ChromaDB
- The metadata store is always: SQLite
- The local inference backend is always: Ollama
- GBNF grammar files live at: .sovereignspec/grammar/*.gbnf

---

Begin generating FILE 1 (README.md) now. After each file, proceed immediately
to the next without pausing. Generate all 22 files in sequence.

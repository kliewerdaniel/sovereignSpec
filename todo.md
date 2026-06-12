# SovereignSpec — Development Todo

> **Goal:** Build the complete SovereignSpec application from scratch.
> All tasks are derived from the documentation in `docs/`, `ARCHITECTURE.md`, and `.sovereignspec/bootstrap.md`.

---

## Phase 0: Project Scaffolding

- [x] Create root `README.md`
- [x] Create `ARCHITECTURE.md`
- [x] Create `CONTRIBUTING.md`
- [x] Create `docs/INSTALLATION.md`
- [x] Create `docs/SPECIFICATION_FORMAT.md`
- [x] Create `docs/CLI_REFERENCE.md`
- [x] Create `docs/AGENT_INTEGRATION.md`
- [x] Create `docs/KNOWLEDGE_GRAPH.md`
- [x] Create `docs/GBNF_GRAMMARS.md`
- [x] Create `docs/SPEC_DRIVEN_WORKFLOW.md`
- [x] Create `docs/SECURITY.md`
- [x] Create `docs/DEVELOPMENT.md`
- [x] Create `docs/adr/ADR-001.md` through `ADR-006.md`
- [x] Create `.sovereignspec/bootstrap.md`
- [x] Create `.sovereignspec/templates/spec-template.sspec`
- [x] Create `.sovereignspec/templates/adr-template.md`
- [x] Create `.sovereignspec/templates/tasks-template.md`
- [ ] Create `pyproject.toml` with package metadata, dependencies, entry points
- [ ] Create `LICENSE` (MIT)
- [ ] Create `.gitignore` (Python, Node, .sovereignspec/memory/)
- [ ] Create `README.md` badges (CI, version, license)
- [ ] Initialize git repository

---

## Phase 1: Python Package Structure

### 1.1 Package Bootstrap

- [ ] Create `sovereignspec/__init__.py` with version string
- [ ] Create `sovereignspec/__main__.py` (allow `python -m sovereignspec`)
- [ ] Configure `pyproject.toml` with:
  - [ ] Package metadata (name, version, author, license)
  - [ ] Dependencies: click/typer, chromadb, pyyaml, pydantic, requests, watchdog
  - [ ] Entry point: `sovereignspec = sovereignspec.cli.main:cli`
  - [ ] Build system (hatchling or setuptools)
- [ ] Create `uv.lock` via `uv sync`

### 1.2 Data Models (`sovereignspec/models/`)

- [ ] `__init__.py` — re-export all models
- [ ] `spec.py` — Pydantic models:
  - [ ] `Specification` — full .sspec model with all 19 fields
  - [ ] `TestCase` — id, description, given, when, then
  - [ ] `PerformanceRequirement` — metric, threshold
  - [ ] `SpecValidationError` — code, message, spec_id
  - [ ] `SpecStatus` — enum (draft|validated|approved|active|implemented|verified|archived)
  - [ ] YAML serialization/deserialization methods
  - [ ] Field validation (max lengths, required checks, kebab-case regex)
- [ ] `graph.py` — Pydantic models:
  - [ ] `GraphNode` — id, type, metadata
  - [ ] `GraphEdge` — source, target, type, weight, metadata
  - [ ] `KnowledgeGraph` — nodes list, edges list, by-id index
  - [ ] `NodeType` — enum (11 types)
  - [ ] `EdgeType` — enum (9 types)
  - [ ] JSON serialization/deserialization
  - [ ] Graph algorithms: add_node, add_edge, topological_sort
- [ ] `task.py` — Pydantic models:
  - [ ] `Task` — id, spec_id, title, description, status, parallel, depends_on, files, acceptance
  - [ ] `TaskList` — spec_id, tasks list
  - [ ] `TaskStatus` — enum (pending|in_progress|completed|blocked|failed)
- [ ] `adr.py` — Pydantic models:
  - [ ] `ADR` — number, title, status, date, context, decision, rationale, alternatives, consequences
  - [ ] `ADRStatus` — enum (proposed|accepted|deprecated|superseded)
  - [ ] Markdown serialization
- [ ] `artifact.py` — Pydantic models:
  - [ ] `ArtifactRecord` — id, task_id, artifact_type, file_path, validated, created_at
  - [ ] `ArtifactRegistry` — agent, project, artifacts list
  - [ ] `ArtifactType` — enum (code|test|doc|config|migration|other)

### 1.3 Persistence Layer (`sovereignspec/persistence/`)

- [ ] `__init__.py`
- [ ] `db.py` — SQLite operations:
  - [ ] `Database` class with connection management
  - [ ] Schema creation (all 10 tables with indexes)
  - [ ] Projects CRUD
  - [ ] Specifications CRUD
  - [ ] Spec relationships CRUD
  - [ ] Spec versions CRUD
  - [ ] ADRs CRUD
  - [ ] Tasks CRUD
  - [ ] Agents CRUD
  - [ ] Artifacts CRUD
  - [ ] Patterns CRUD
  - [ ] Sessions CRUD
  - [ ] Migration framework (versioned SQL files)
  - [ ] Connection pooling / WAL mode
- [ ] `chroma.py` — ChromaDB operations:
  - [ ] `ChromaStore` class
  - [ ] Collection management (specs, adrs, patterns)
  - [ ] Embedding function (wraps Ollama embeddings API)
  - [ ] Document addition with metadata
  - [ ] Similarity search with filtering
  - [ ] Collection stats (count, last indexed)
  - [ ] Persistence path configuration
- [ ] `migrations/001_initial.sql` — Initial schema creation

### 1.4 Engine (`sovereignspec/engine/`)

- [ ] `__init__.py`
- [ ] `grammar.py` — GBNF management:
  - [ ] `load_grammar(name: str) -> str`
  - [ ] `generate_structured(prompt, grammar_name, model, temperature) -> dict`
  - [ ] `generate_streaming(prompt, grammar_name, model) -> Generator[str]`
  - [ ] Ollama client wrapper (REST API calls)
  - [ ] Error handling (model not found, timeout, grammar errors)
- [ ] `validator.py` — Spec validation:
  - [ ] `Validator` class with rule registry
  - [ ] Rule: MISSING_PURPOSE
  - [ ] Rule: AMBIGUOUS_REQUIREMENTS
  - [ ] Rule: UNDEFINED_DEPENDENCY
  - [ ] Rule: MISSING_ACCEPTANCE_CRITERIA
  - [ ] Rule: MISSING_TEST_CASES
  - [ ] Rule: CONTRADICTS_EXISTING_SPEC (LLM-driven)
  - [ ] Rule: DEPENDENCY_CYCLE (graph-based)
  - [ ] Rule: NARRATIVE_DRIFT (embedding-based)
  - [ ] Rule: INCOMPLETE_SECURITY
  - [ ] Rule: DUPLICATE_ID
  - [ ] Rule: INVALID_STATUS_TRANSITION
  - [ ] Rule: MISSING_CONSTRAINTS
  - [ ] `ValidationContext` — carries DB, graph, and LLM references
  - [ ] `validate_spec(spec, context) -> list[ValidationError]`
  - [ ] `validate_all(context) -> dict[spec_id, list[ValidationError]]`
- [ ] `compiler.py` — Spec compiler pipeline:
  - [ ] `Compiler` class — orchestrates all 12 steps
  - [ ] Step 1: Parse .sspec YAML
  - [ ] Step 2: Validate fields
  - [ ] Step 3: Resolve dependency graph (topological sort)
  - [ ] Step 4: Check contradictions
  - [ ] Step 5: Compute drift score
  - [ ] Step 6: Generate implementation plan (LLM + grammar)
  - [ ] Step 7: Generate task tree
  - [ ] Step 8: Generate agent context
  - [ ] Step 9: Generate documentation bundle
  - [ ] Step 10: Update knowledge graph
  - [ ] Step 11: Update ChromaDB embeddings
  - [ ] Step 12: Commit version record to SQLite
  - [ ] `compile_spec(spec_id, context) -> CompilationResult`
  - [ ] `compile_all(context) -> dict[spec_id, CompilationResult]`
  - [ ] Dry-run mode
  - [ ] Rollback support
- [ ] `graph.py` — Knowledge graph operations:
  - [ ] Load/save adjacency JSON
  - [ ] `add_node(id, type, metadata) -> str`
  - [ ] `add_edge(source, target, type, weight, metadata) -> str`
  - [ ] `what_breaks_if_changed(spec_id, max_depth=3) -> list[Node]`
  - [ ] `what_specs_affect_module(module_path) -> list[Specification]`
  - [ ] `which_adr_created_architecture(pattern_name) -> list[ADR]`
  - [ ] `dependency_chain(spec_id, max_depth=5) -> dict`
  - [ ] `find_contradictions() -> list[ContradictionPair]`
  - [ ] `compute_drift_score(spec_id, constitution_text) -> float`
  - [ ] Neo4j optional backend support
  - [ ] NetworkX integration
- [ ] `rag.py` — RAG pipeline:
  - [ ] `embed_text(text: str) -> list[float]` (via Ollama)
  - [ ] `search_specs(query: str, n_results: int) -> list[dict]`
  - [ ] `search_adrs(query: str, n_results: int) -> list[dict]`
  - [ ] `search_patterns(query: str, n_results: int) -> list[dict]`
  - [ ] `build_context(spec_id: str) -> str` — assemble RAG context for LLM
  - [ ] Chunking strategy (by section, 512-token overlap)
- [ ] `contradiction.py` — Contradiction detection:
  - [ ] `ContradictionDetector` class
  - [ ] Phase 1: Candidate identification via ChromaDB similarity
  - [ ] Phase 2: LLM analysis with contradiction_report.gbnf grammar
  - [ ] Phase 3: Graph integration (CONFLICTS_WITH edges)
  - [ ] Phase 4: Cross-validation against acceptance criteria
  - [ ] `detect(spec_id) -> list[ContradictionPair]`
  - [ ] `detect_all() -> list[ContradictionPair]`
- [ ] `drift.py` — Narrative drift tracking:
  - [ ] `DriftTracker` class
  - [ ] Phase 1: Constitution embedding (one-time)
  - [ ] Phase 2: Spec scoring on compile
  - [ ] Phase 3: Threshold check (flag < 0.6)
  - [ ] Phase 4: Trend analysis across versions
  - [ ] Phase 5: Aggregate project-level scoring
  - [ ] `compute_drift(spec_id) -> DriftReport`
  - [ ] `project_drift_summary() -> DriftSummary`
- [ ] `repository.py` — Repository intelligence:
  - [ ] `RepositoryMapper` class
  - [ ] Directory tree walk with .gitignore respect
  - [ ] Language detection via extension map
  - [ ] Entrypoint detection (main.*, index.*, app.*)
  - [ ] Module boundary detection (package.json, __init__.py, Cargo.toml)
  - [ ] repository_map.json generation
  - [ ] `PatternExtractor` class
  - [ ] Pattern: naming conventions (camelCase, PascalCase, snake_case)
  - [ ] Pattern: error handling (try/catch, error classes)
  - [ ] Pattern: test file naming (*.test.ts, *.spec.ts)
  - [ ] Pattern: import organization (external → internal → relative)
  - [ ] Pattern: API route conventions
  - [ ] Pattern: database patterns
  - [ ] pattern_library.json generation
  - [ ] File watcher integration (watchdog)

### 1.5 Agent Adapters (`sovereignspec/adapters/`)

- [ ] `__init__.py` — Adapter registry + factory function
- [ ] `base.py` — `AgentAdapter` abstract base class:
  - [ ] `name: str` property
  - [ ] `write_integration_files(project_dir) -> list[str]`
  - [ ] `generate_command_templates() -> dict[str, str]`
  - [ ] `artifact_path(project_dir, agent_name) -> str`
- [ ] `claude_code.py` — Claude Code adapter:
  - [ ] Write `CLAUDE.md`
  - [ ] Write `.claude/commands/sovereign-constitution.md`
  - [ ] Write `.claude/commands/sovereign-specify.md`
  - [ ] Write `.claude/commands/sovereign-clarify.md`
  - [ ] Write `.claude/commands/sovereign-plan.md`
  - [ ] Write `.claude/commands/sovereign-tasks.md`
  - [ ] Write `.claude/commands/sovereign-analyze.md`
  - [ ] Write `.claude/commands/sovereign-implement.md`
  - [ ] Write `.claude/commands/sovereign-checklist.md`
- [ ] `opencode.py` — OpenCode adapter:
  - [ ] Write `AGENTS.md` with full contract and commands
- [ ] `cursor.py` — Cursor adapter:
  - [ ] Write `.cursor/rules/sovereignspec.mdc`
- [ ] `cline.py` — Cline adapter:
  - [ ] Write `.clinerules`
- [ ] `roocode.py` — RooCode adapter:
  - [ ] Write `.roo/rules.md`
- [ ] `codex.py` — Codex CLI adapter:
  - [ ] Write `AGENTS.md`
  - [ ] Write skills files
- [ ] `gemini_cli.py` — Gemini CLI adapter:
  - [ ] Write `GEMINI.md`
- [ ] `aider.py` — Aider adapter:
  - [ ] Write `.aider.conf.yml`
- [ ] `windsurf.py` — Windsurf adapter:
  - [ ] Write `.windsurfrules`
- [ ] `continue_.py` — Continue adapter:
  - [ ] Write `.continue/config.json`
  - [ ] Write `.continue/commands/`
- [ ] `generic.py` — Generic filesystem adapter:
  - [ ] Write `.sovereignspec/bootstrap.md` reference only

---

## Phase 2: CLI Implementation

### 2.1 CLI Framework

- [ ] Create `sovereignspec/cli/__init__.py`
- [ ] Create `sovereignspec/cli/main.py`:
  - [ ] Click/Typer root group
  - [ ] Global flags: `--project-dir`, `--model`, `--verbose`, `--json`
  - [ ] Environment variable loading
  - [ ] Error handling with exit codes (0-5)
  - [ ] Version display

### 2.2 Commands

- [ ] `commands/init.py`:
  - [ ] `init [path]` — Create project structure
  - [ ] Copy templates, grammar files, bootstrap.md
  - [ ] Create .sovereignspec/ directory tree
  - [ ] Generate config.json with defaults
  - [ ] `--force`, `--model`, `--adapter` options
- [ ] `commands/spec.py`:
  - [ ] `spec create <spec-id>` — Create .sspec file from template
  - [ ] `spec validate <spec-id> | --all` — Run validation rules
  - [ ] `spec compile <spec-id> | --all` — Run compiler pipeline
  - [ ] `spec list [--status]` — List specs with filtering
  - [ ] `spec diff <spec-id> [--version] [--version]` — Semantic diff
  - [ ] `spec graph <spec-id>` — ASCII graph visualization
- [ ] `commands/sovereign.py` — The /sovereign.* workflow:
  - [ ] `sovereign-constitution [description]` — LLM-generate constitution
  - [ ] `specify [description]` — LLM-generate .sspec from description
  - [ ] `clarify <spec-id>` — Interactive RAG-grounded Q&A
  - [ ] `plan <spec-id> [--tech-stack]` — Generate implementation plan
  - [ ] `tasks <spec-id>` — Generate task decomposition
  - [ ] `analyze <spec-id> | --all` — Contradiction + drift analysis
  - [ ] `implement <spec-id>` — Build agent context package
- [ ] `commands/graph.py`:
  - [ ] `graph query --what-breaks <spec-id>` — Impact analysis
  - [ ] `graph query --affects-module <path>` — Module traceability
  - [ ] `graph stats` — Node/edge counts, type distribution
- [ ] `commands/context.py`:
  - [ ] `context build <spec-id> [--agent]` — Assemble context package
- [ ] `commands/adr.py`:
  - [ ] `adr create [--title] [--context]` — Create ADR from template
  - [ ] `adr list` — List all ADRs with status
- [ ] `commands/memory.py`:
  - [ ] `memory sync [--rebuild-graph] [--rebuild-embeddings]` — Sync stores
  - [ ] `memory status` — Show store sizes and counts
- [ ] `commands/repo.py`:
  - [ ] `repo map [--rebuild]` — Generate repository map
  - [ ] `repo patterns` — Display extracted patterns
- [ ] `commands/docs.py`:
  - [ ] `docs generate <spec-id> | --all [--format]` — Generate docs

### 2.3 Diagnostics

- [ ] `doctor` command:
  - [ ] Python version check
  - [ ] Ollama connectivity check
  - [ ] Model availability check
  - [ ] ChromaDB availability check
  - [ ] SQLite availability check
  - [ ] Filesystem permissions check
  - [ ] Repair mode functionality

---

## Phase 3: GBNF Grammar Files

### 3.1 Create Grammar Files

- [ ] `.sovereignspec/grammar/spec_validation_result.gbnf`
- [ ] `.sovereignspec/grammar/implementation_plan.gbnf`
- [ ] `.sovereignspec/grammar/task_list.gbnf`
- [ ] `.sovereignspec/grammar/api_spec.gbnf`
- [ ] `.sovereignspec/grammar/adr.gbnf`
- [ ] `.sovereignspec/grammar/test_case.gbnf`
- [ ] `.sovereignspec/grammar/contradiction_report.gbnf`
- [ ] `.sovereignspec/grammar/drift_report.gbnf`

### 3.2 Grammar Tests

- [ ] Unit test: each grammar produces valid JSON for known inputs
- [ ] Unit test: each grammar rejects invalid outputs
- [ ] Integration test: Ollama with grammar produces parseable output

---

## Phase 4: Testing

### 4.1 Unit Tests

- [ ] `tests/unit/test_models_spec.py` — Specification model validation
- [ ] `tests/unit/test_models_graph.py` — Graph model CRUD
- [ ] `tests/unit/test_validator.py` — All 12 rules with pass/fail cases
- [ ] `tests/unit/test_compiler.py` — Pipeline step execution (mocked LLM)
- [ ] `tests/unit/test_graph.py` — Graph algorithms (traversal, dependency)
- [ ] `tests/unit/test_grammar.py` — Grammar loading and structure
- [ ] `tests/unit/test_rag.py` — ChromaDB operations (ephemeral client)
- [ ] `tests/unit/test_contradiction.py` — Detection algorithm
- [ ] `tests/unit/test_drift.py` — Drift scoring algorithm
- [ ] `tests/unit/test_repository.py` — File walking, language detection
- [ ] `tests/unit/test_adapters.py` — Each adapter writes correct files
- [ ] `tests/unit/test_db.py` — SQLite CRUD for all tables

### 4.2 Integration Tests

- [ ] `tests/integration/test_init_project.py` — Full init workflow
- [ ] `tests/integration/test_spec_lifecycle.py` — Create → validate → compile flow
- [ ] `tests/integration/test_agent_integration.py` — Integration file generation
- [ ] `tests/integration/test_graph_persistence.py` — Save/load graph.json

### 4.3 LLM-in-the-Loop Tests

- [ ] `tests/integration/test_llm_grammar.py` — Real Ollama grammar enforcement
- [ ] `tests/integration/test_llm_contradiction.py` — Real contradiction detection
- [ ] `tests/integration/test_llm_plan_generation.py` — Real plan generation

### 4.4 Test Configuration

- [ ] `pyproject.toml` pytest configuration
- [ ] `conftest.py` with fixtures (tmp project, mock LLM, ephemeral ChromaDB)
- [ ] Test fixtures in `tests/fixtures/`:
  - [ ] `sample-spec.sspec` — Valid spec for testing
  - [ ] `sample-constitution.md` — Sample constitution
  - [ ] `sample-graph.json` — Sample graph for graph tests

---

## Phase 5: UI — Next.js Application

### 5.1 Project Setup

- [ ] Initialize `ui/` with `pnpm create next-app`
- [ ] Configure TypeScript strict mode
- [ ] Install and configure Tailwind CSS
- [ ] Install and configure shadcn/ui
- [ ] Set up project path aliases

### 5.2 Core Layout

- [ ] Root layout with sidebar navigation
- [ ] Theme provider (light/dark)
- [ ] Responsive design system

### 5.3 Pages

- [ ] **Dashboard** (`/`):
  - [ ] Project list with status badges
  - [ ] Recent activity feed
  - [ ] Spec health overview (passing/failing counts)
  - [ ] Quick-action buttons
- [ ] **Project View** (`/projects/[id]`):
  - [ ] Project header with metadata
  - [ ] Spec list with status filters
  - [ ] ADR list
  - [ ] Task summary
  - [ ] Agent activity log
- [ ] **Specification Browser** (`/specs`):
  - [ ] Spec table with sorting
  - [ ] Status filter dropdown
  - [ ] Search/filter by tag
  - [ ] Drift score indicators
- [ ] **Spec Detail** (`/specs/[id]`):
  - [ ] Full spec content rendered
  - [ ] Graph visualization (mini)
  - [ ] Related items panel
  - [ ] Version history timeline
  - [ ] Task status summary
- [ ] **Spec Editor** (`/specs/new`):
  - [ ] YAML editor with syntax highlighting
  - [ ] Live field validation
  - [ ] Field-level error messages
  - [ ] Save button with validation summary
- [ ] **Knowledge Graph Explorer** (`/graph`):
  - [ ] Interactive force-directed graph (D3.js or vis-network)
  - [ ] Node type color coding
  - [ ] Click to inspect node details
  - [ ] Filter by node type
  - [ ] Search nodes
- [ ] **Task Board** (`/tasks`):
  - [ ] Kanban columns (pending, in_progress, completed)
  - [ ] Drag-and-drop task reordering
  - [ ] Task detail modal
  - [ ] Filter by spec
- [ ] **Documentation Hub** (`/docs`):
  - [ ] File tree browser
  - [ ] Markdown renderer
  - [ ] Full-text search
- [ ] **Settings** (`/settings`):
  - [ ] Ollama model configuration
  - [ ] Agent adapter selection
  - [ ] ChromaDB path configuration
  - [ ] File watcher toggle
  - [ ] Health check display

### 5.4 API Routes

- [ ] `GET /api/projects` — List projects
- [ ] `GET /api/projects/:id` — Project details
- [ ] `GET /api/specs` — List specs (with filter)
- [ ] `GET /api/specs/:id` — Spec detail
- [ ] `POST /api/specs` — Create spec
- [ ] `GET /api/graph` — Full graph
- [ ] `GET /api/graph/query` — Graph queries
- [ ] `GET /api/tasks` — Task list
- [ ] `PUT /api/tasks/:id` — Update task
- [ ] `GET /api/docs` — Doc tree
- [ ] `GET /api/settings` — Get config
- [ ] `PUT /api/settings` — Update config
- [ ] `GET /api/health` — System health

### 5.5 Components

- [ ] `ui/` — shadcn/ui base components (button, card, input, select, table, etc.)
- [ ] `spec-editor.tsx` — YAML editor with validation
- [ ] `graph-visualization.tsx` — D3.js force-directed graph
- [ ] `task-board.tsx` — Kanban board
- [ ] `project-card.tsx` — Project summary card
- [ ] `agent-status.tsx` — Agent session display
- [ ] `spec-health-badge.tsx` — Validation status indicator
- [ ] `diff-viewer.tsx` — Spec version diff display

---

## Phase 6: Integration and Polish

### 6.1 End-to-End Workflow Testing

- [ ] Full pipeline: init → constitution → specify → clarify → plan → tasks → analyze → implement
- [ ] Multi-spec dependency resolution
- [ ] Contradiction detection and resolution
- [ ] Spec evolution (versioning, rollback, superseding)
- [ ] Drift detection and remediation
- [ ] ADR creation and linking
- [ ] Artifact submission and validation
- [ ] Knowledge graph persistence and querying

### 6.2 Error Handling and Edge Cases

- [ ] Ollama unavailable → clear error message
- [ ] ChromaDB corruption → repair flow
- [ ] SQLite locked → retry with backoff
- [ ] Malformed .sspec YAML → parse error with line number
- [ ] Circular dependencies → detected and reported
- [ ] Missing dependencies → dependency validation error
- [ ] Large spec (>100 requirements) → reasonable performance
- [ ] Empty project → graceful handling
- [ ] Non-initialized directory → "run init first" message
- [ ] Permission denied → actionable error

### 6.3 Performance Optimization

- [ ] ChromaDB query caching
- [ ] SQLite connection pooling / WAL mode
- [ ] Graph serialization with incremental updates
- [ ] Embedding caching (avoid re-embedding unchanged specs)
- [ ] Lazy loading of ChromaDB collections
- [ ] File watcher debounce tuning

### 6.4 Documentation Verification

- [ ] Every CLI command documented matches implementation
- [ ] Every config field documented matches config.json schema
- [ ] Every validation error code documented exists in code
- [ ] Every adapter file documented is generated by the adapter
- [ ] Every GBNF grammar documented exists in grammar/
- [ ] Every node/edge type documented exists in graph model

---

## Phase 7: Release

### 7.1 Pre-Release

- [ ] Full test suite pass (unit + integration)
- [ ] Lint and type check pass
- [ ] Coverage thresholds met (80%+)
- [ ] CHANGELOG.md written
- [ ] Version bumped in pyproject.toml

### 7.2 Build and Publish

- [ ] `uv build` — Build wheel and sdist
- [ ] `uv publish` — Publish to PyPI
- [ ] Git tag `v1.0.0`
- [ ] GitHub release with release notes

### 7.3 Post-Release

- [ ] Verify `uv tool install sovereignspec` works on clean machine
- [ ] Verify `sovereignspec init` creates correct structure
- [ ] Verify `sovereignspec doctor` reports healthy
- [ ] Verify `sovereignspec integrate --agent claude-code` writes correct files

---

## Legend

- `[ ]` — Not started
- `[/]` — In progress
- `[x]` — Completed

---

## Progress Summary

| Phase | Tasks | Completed |
|-------|-------|-----------|
| Phase 0: Scaffolding | 17 | 17 |
| Phase 1: Python Package | ~120 | 0 |
| Phase 2: CLI | ~50 | 0 |
| Phase 3: GBNF Grammars | 10 | 0 |
| Phase 4: Testing | ~40 | 0 |
| Phase 5: UI | ~50 | 0 |
| Phase 6: Polish | ~25 | 0 |
| Phase 7: Release | ~10 | 0 |
| **Total** | **~322** | **17** |

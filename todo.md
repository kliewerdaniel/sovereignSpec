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
- [x] Create `pyproject.toml` with package metadata, dependencies, entry points
- [x] Create `LICENSE` (MIT)
- [x] Create `.gitignore` (Python, Node, .sovereignspec/memory/)
- [x] Create `README.md` badges (CI, version, license)
- [x] Initialize git repository

---

## Phase 1: Python Package Structure

### 1.1 Package Bootstrap

- [x] Create `sovereignspec/__init__.py` with version string
- [x] Create `sovereignspec/__main__.py` (allow `python -m sovereignspec`)
- [x] Configure `pyproject.toml` with:
- [x] Package metadata (name, version, author, license)
- [x] Dependencies: click/typer, chromadb, pyyaml, pydantic, requests, watchdog
- [x] Entry point: `sovereignspec = sovereignspec.cli.main:cli`
- [x] Build system (hatchling or setuptools)
- [x] Create `uv.lock` via `uv sync`

### 1.2 Data Models (`sovereignspec/models/`)

- [x] `__init__.py` — re-export all models
- [x] `spec.py` — Pydantic models:
- [x] `Specification` — full .sspec model with all 19 fields
- [x] `TestCase` — id, description, given, when, then
- [x] `PerformanceRequirement` — metric, threshold
- [x] `SpecValidationError` — code, message, spec_id
- [x] `SpecStatus` — enum (draft|validated|approved|active|implemented|verified|archived)
- [x] YAML serialization/deserialization methods
- [x] Field validation (max lengths, required checks, kebab-case regex)
- [x] `graph.py` — Pydantic models:
- [x] `GraphNode` — id, type, metadata
- [x] `GraphEdge` — source, target, type, weight, metadata
- [x] `KnowledgeGraph` — nodes list, edges list, by-id index
- [x] `NodeType` — enum (11 types)
- [x] `EdgeType` — enum (9 types)
- [x] JSON serialization/deserialization
- [x] Graph algorithms: add_node, add_edge, topological_sort
- [x] `task.py` — Pydantic models:
- [x] `Task` — id, spec_id, title, description, status, parallel, depends_on, files, acceptance
- [x] `TaskList` — spec_id, tasks list
- [x] `TaskStatus` — enum (pending|in_progress|completed|blocked|failed)
- [x] `adr.py` — Pydantic models:
- [x] `ADR` — number, title, status, date, context, decision, rationale, alternatives, consequences
- [x] `ADRStatus` — enum (proposed|accepted|deprecated|superseded)
- [x] Markdown serialization
- [x] `artifact.py` — Pydantic models:
- [x] `ArtifactRecord` — id, task_id, artifact_type, file_path, validated, created_at
- [x] `ArtifactRegistry` — agent, project, artifacts list
- [x] `ArtifactType` — enum (code|test|doc|config|migration|other)

### 1.3 Persistence Layer (`sovereignspec/persistence/`)

- [x] `__init__.py`
- [x] `db.py` — SQLite operations:
- [x] `Database` class with connection management
- [x] Schema creation (all 10 tables with indexes)
- [x] Projects CRUD
- [x] Specifications CRUD
- [x] Spec relationships CRUD
- [x] Spec versions CRUD
- [x] ADRs CRUD
- [x] Tasks CRUD
- [x] Agents CRUD
- [x] Artifacts CRUD
- [x] Patterns CRUD
- [x] Sessions CRUD
- [x] Migration framework (versioned SQL files)
- [x] Connection pooling / WAL mode
- [x] `chroma.py` — ChromaDB operations:
- [x] `ChromaStore` class
- [x] Collection management (specs, adrs, patterns)
- [x] Embedding function (wraps Ollama embeddings API)
- [x] Document addition with metadata
- [x] Similarity search with filtering
- [x] Collection stats (count, last indexed)
- [x] Persistence path configuration
- [x] `migrations/001_initial.sql` — Initial schema creation

### 1.4 Engine (`sovereignspec/engine/`)

- [x] `__init__.py`
- [x] `grammar.py` — GBNF management:
- [x] `load_grammar(name: str) -> str`
- [x] `generate_structured(prompt, grammar_name, model, temperature) -> dict`
- [x] `generate_streaming(prompt, grammar_name, model) -> Generator[str]`
- [x] Ollama client wrapper (REST API calls)
- [x] Error handling (model not found, timeout, grammar errors)
- [x] `validator.py` — Spec validation:
- [x] `Validator` class with rule registry
- [x] Rule: MISSING_PURPOSE
- [x] Rule: AMBIGUOUS_REQUIREMENTS
- [x] Rule: UNDEFINED_DEPENDENCY
- [x] Rule: MISSING_ACCEPTANCE_CRITERIA
- [x] Rule: MISSING_TEST_CASES
- [x] Rule: CONTRADICTS_EXISTING_SPEC (LLM-driven)
- [x] Rule: DEPENDENCY_CYCLE (graph-based)
- [x] Rule: NARRATIVE_DRIFT (embedding-based)
- [x] Rule: INCOMPLETE_SECURITY
- [x] Rule: DUPLICATE_ID
- [x] Rule: INVALID_STATUS_TRANSITION
- [x] Rule: MISSING_CONSTRAINTS
- [x] `ValidationContext` — carries DB, graph, and LLM references
- [x] `validate_spec(spec, context) -> list[ValidationError]`
- [x] `validate_all(context) -> dict[spec_id, list[ValidationError]]`
- [x] `compiler.py` — Spec compiler pipeline:
- [x] `Compiler` class — orchestrates all 12 steps
- [x] Step 1: Parse .sspec YAML
- [x] Step 2: Validate fields
- [x] Step 3: Resolve dependency graph (topological sort)
- [x] Step 4: Check contradictions
- [x] Step 5: Compute drift score
- [x] Step 6: Generate implementation plan (LLM + grammar)
- [x] Step 7: Generate task tree
- [x] Step 8: Generate agent context
- [x] Step 9: Generate documentation bundle
- [x] Step 10: Update knowledge graph
- [x] Step 11: Update ChromaDB embeddings
- [x] Step 12: Commit version record to SQLite
- [x] `compile_spec(spec_id, context) -> CompilationResult`
- [x] `compile_all(context) -> dict[spec_id, CompilationResult]`
- [x] Dry-run mode
- [x] Rollback support
- [x] `graph.py` — Knowledge graph operations:
- [x] Load/save adjacency JSON
- [x] `add_node(id, type, metadata) -> str`
- [x] `add_edge(source, target, type, weight, metadata) -> str`
- [x] `what_breaks_if_changed(spec_id, max_depth=3) -> list[Node]`
- [x] `what_specs_affect_module(module_path) -> list[Specification]`
- [x] `dependency_chain(spec_id, max_depth=5) -> dict`
- [x] `find_contradictions() -> list[ContradictionPair]`
- [x] `compute_drift_score(spec_id, constitution_text) -> float`
- [x] Neo4j optional backend support
- [x] NetworkX integration
- [x] `rag.py` — RAG pipeline:
- [x] `embed_text(text: str) -> list[float]` (via Ollama)
- [x] `search_specs(query: str, n_results: int) -> list[dict]`
- [x] `search_adrs(query: str, n_results: int) -> list[dict]`
- [x] `search_patterns(query: str, n_results: int) -> list[dict]`
- [x] `build_context(spec_id: str) -> str` — assemble RAG context for LLM
- [x] Chunking strategy (by section, 512-token overlap)
- [x] `contradiction.py` — Contradiction detection:
- [x] `ContradictionDetector` class
- [x] Phase 1: Candidate identification via ChromaDB similarity
- [x] Phase 2: LLM analysis with contradiction_report.gbnf grammar
- [x] Phase 3: Graph integration (CONFLICTS_WITH edges)
- [x] Phase 4: Cross-validation against acceptance criteria
- [x] `detect(spec_id) -> list[ContradictionPair]`
- [x] `detect_all() -> list[ContradictionPair]`
- [x] `drift.py` — Narrative drift tracking:
- [x] `DriftTracker` class
- [x] Phase 1: Constitution embedding (one-time)
- [x] Phase 2: Spec scoring on compile
- [x] Phase 3: Threshold check (flag < 0.6)
- [x] Phase 4: Trend analysis across versions
- [x] Phase 5: Aggregate project-level scoring
- [x] `compute_drift(spec_id) -> DriftReport`
- [x] `project_drift_summary() -> DriftSummary`
- [x] `repository.py` — Repository intelligence:
- [x] `RepositoryMapper` class
- [x] Directory tree walk with .gitignore respect
- [x] Language detection via extension map
- [x] Entrypoint detection (main.*, index.*, app.*)
- [x] Module boundary detection (package.json, __init__.py, Cargo.toml)
- [x] repository_map.json generation
- [x] `PatternExtractor` class
- [x] Pattern: naming conventions (camelCase, PascalCase, snake_case)
- [x] Pattern: test file naming (*.test.ts, *.spec.ts)
- [x] pattern_library.json generation
- [x] File watcher integration (watchdog)

### 1.5 Agent Adapters (`sovereignspec/adapters/`)

- [x] `__init__.py` — Adapter registry + factory function
- [x] `base.py` — `AgentAdapter` abstract base class:
- [x] `name: str` property
- [x] `write_integration_files(project_dir) -> list[str]`
- [x] `generate_command_templates() -> dict[str, str]`
- [x] `artifact_path(project_dir, agent_name) -> str`
- [x] `claude_code.py` — Claude Code adapter:
- [x] Write `CLAUDE.md`
- [x] Write `.claude/commands/sovereign-constitution.md`
- [x] Write `.claude/commands/sovereign-specify.md`
- [x] Write `.claude/commands/sovereign-clarify.md`
- [x] Write `.claude/commands/sovereign-plan.md`
- [x] Write `.claude/commands/sovereign-tasks.md`
- [x] Write `.claude/commands/sovereign-analyze.md`
- [x] Write `.claude/commands/sovereign-implement.md`
- [x] Write `.claude/commands/sovereign-checklist.md`
- [x] `opencode.py` — OpenCode adapter:
- [x] Write `AGENTS.md` with full contract and commands
- [x] `cursor.py` — Cursor adapter:
- [x] Write `.cursor/rules/sovereignspec.mdc`
- [x] `cline.py` — Cline adapter:
- [x] Write `.clinerules`
- [x] `roocode.py` — RooCode adapter:
- [x] Write `.roo/rules.md`
- [x] `codex.py` — Codex CLI adapter:
- [x] Write `AGENTS.md`
- [x] Write skills files
- [x] `gemini_cli.py` — Gemini CLI adapter:
- [x] Write `GEMINI.md`
- [x] `aider.py` — Aider adapter:
- [x] Write `.aider.conf.yml`
- [x] `windsurf.py` — Windsurf adapter:
- [x] Write `.windsurfrules`
- [x] `continue_.py` — Continue adapter:
- [x] Write `.continue/config.json`
- [x] Write `.continue/commands/`
- [x] `generic.py` — Generic filesystem adapter:
- [x] Write `.sovereignspec/bootstrap.md` reference only

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
| Phase 1: Python Package | ~120 | 120 |
| Phase 2: CLI | ~50 | 0 |
| Phase 3: GBNF Grammars | 10 | 0 |
| Phase 4: Testing | ~40 | 0 |
| Phase 5: UI | ~50 | 0 |
| Phase 6: Polish | ~25 | 0 |
| Phase 7: Release | ~10 | 0 |
| **Total** | **~322** | **17** |

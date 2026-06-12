# SovereignSpec Agent Integration Guide

**Version 1.0.0**

---

## 1. The Agent Contract

Every coding agent integrated with SovereignSpec must honor the following contract. This contract is enforced through the filesystem — SovereignSpec writes files, agents read them, agents write files, SovereignSpec reads them.

### Required Behaviors

Any agent working in a SovereignSpec project must:

1. **Read specifications before writing any code.** Always start by reading the active `.sspec` files in `.sovereignspec/specs/`. Understand all requirements, constraints, and acceptance criteria before generating code.

2. **Update implementation status in task files upon task completion.** After implementing a task, update `.sovereignspec/tasks/{spec-id}-tasks.md` by marking the task as `[x]` and adding a completion note.

3. **Generate tests for every implemented feature.** For every feature implemented, generate tests that validate the spec's acceptance criteria. Test files are registered as artifacts.

4. **Generate documentation for every module changed.** Document any new or modified module. Documentation is registered as an artifact.

5. **Update `.sovereignspec/graph/graph.json` with new relationship edges.** After implementation, add edges connecting implemented nodes (modules, endpoints, etc.) to the spec node.

6. **Record all architectural decisions as ADR drafts.** If implementation reveals a significant architectural decision not covered by existing ADRs, create a draft ADR at `.sovereignspec/adr/ADR-NNN.md`.

7. **Submit artifact paths to `.sovereignspec/agents/{agent-name}/artifacts.json`.** Register every generated file (code, test, doc, config) in the artifact registry.

---

## 2. The bootstrap.md Universal Contract

The `.sovereignspec/bootstrap.md` file is the universal contract that any file-aware coding agent can read. Below is its complete content (also available at `.sovereignspec/bootstrap.md` in every initialized project):

```markdown
# SovereignSpec Project Contract

## What is SovereignSpec?
SovereignSpec is a local-first Specification-Driven Development (SDD) engine.
This project uses SovereignSpec to manage its specifications, architecture decisions,
tasks, and knowledge graph. All specifications are in `.sspec` files.
All implementation is driven by these specifications.

## Your Role
You are a coding agent working within this SovereignSpec project. Your task is to
read the project's specifications, understand the requirements and constraints,
and implement code that satisfies the acceptance criteria. The specification
is the source of truth — the code is disposable.

## Required Reading (in order)
Before implementing anything, read these files:

1. `.sovereignspec/constitution.md` — Project governing principles
2. `.sovereignspec/specs/` — All active `.sspec` specification files
3. `.sovereignspec/adr/` — Architecture Decision Records
4. `.sovereignspec/tasks/active_tasks.md` — Current work units
5. `.sovereignspec/patterns/pattern_library.json` — Coding conventions
6. `.sovereignspec/patterns/repository_map.json` — Repository structure

## The Agent Contract
For every task, you must:

1. Read specifications before writing any code
2. Update task status in `.sovereignspec/tasks/{spec-id}-tasks.md` upon completion
3. Generate tests for every implemented feature
4. Generate documentation for every module changed
5. Honor all constraints listed in active specs
6. Update `.sovereignspec/graph/graph.json` with new relationships
7. Record all new architectural decisions as ADR drafts
8. Register artifacts in `.sovereignspec/agents/{agent-name}/artifacts.json`

## Specification Format (.sspec) Quick Reference
- `id` (string, required): kebab-case unique identifier
- `title` (string, required): human-readable title
- `version` (semver, required): e.g. "1.0.0"
- `status` (enum, required): draft|validated|approved|active|implemented|verified|archived
- `purpose` (string, required): 1-3 sentence description
- `requirements` (list[string], required): functional requirements
- `constraints` (list[string], required): hard limits
- `acceptance_criteria` (list[string], required): testable pass/fail criteria
- `dependencies` (list[string], required): spec IDs this depends on
- `test_cases` (list[object], required): structured test definitions
- `security_requirements` (list[string], optional): security controls
- `performance_requirements` (list[object], optional): performance targets
- `architecture_notes` (string, optional): architectural guidance
- `implementation_hints` (list[string], optional): implementation guidance

## Task File Format
Tasks are in `.sovereignspec/tasks/{spec-id}-tasks.md`:

```markdown
# Tasks: {spec-id} v{version}

## [P] Task 1: Title
Description of the task.
Status: [ ] pending
Files to create/modify:
  - path/to/file.ts
Acceptance: What must be true for this task to be complete

## Task 2: Title (depends on Task 1)
...
```

`[P]` marks tasks that can run in parallel with their siblings.

## Artifact Submission
After completing a task, register artifacts in:
`.sovereignspec/agents/{agent-name}/artifacts.json`

```json
{
  "agent": "your-agent-name",
  "artifacts": [
    {
      "id": "uuid",
      "task_id": "task-uuid",
      "artifact_type": "code|test|doc|config|migration",
      "file_path": "src/auth/jwt.ts",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

## ADR Creation
When you discover a significant architectural decision not covered by existing ADRs:
1. Find the next ADR number (check existing files in `.sovereignspec/adr/`)
2. Create `.sovereignspec/adr/ADR-NNN.md` using this template:
   ```markdown
   # ADR-NNN: Title
   Status: proposed
   Date: YYYY-MM-DD
   Context: ...
   Decision: ...
   Consequences: ...
   ```

## Constraints You Must Never Violate
- Do not modify `.sspec` files (specs are upstream artifacts)
- Do not delete architecture decision records
- Do not modify `graph.json` node definitions without creating corresponding edges
- Do not implement features that are not specified in an active `.sspec`
- Do not use external APIs or cloud services (this is a local-first project)
- Do not introduce dependencies not listed or implied by the specs
- All secrets, keys, and tokens must be environment-variable configured

## Graph Update Procedure
After implementation, update `.sovereignspec/graph/graph.json`:
1. Add a node for each new module or endpoint created
2. Add `REFERENCES` edges from the spec to new nodes
3. Add `IMPLEMENTS` edges from tasks to the spec
4. If a new ADR was created, add a `REFERENCES` edge from the spec to the ADR
```

---

## 3. Per-Agent Integration

### 3.1 Claude Code

**Files Written by SovereignSpec:**

- `CLAUDE.md` — Project-level instructions
- `.claude/commands/sovereign-constitution.md`
- `.claude/commands/sovereign-specify.md`
- `.claude/commands/sovereign-clarify.md`
- `.claude/commands/sovereign-plan.md`
- `.claude/commands/sovereign-tasks.md`
- `.claude/commands/sovereign-analyze.md`
- `.claude/commands/sovereign-implement.md`
- `.claude/commands/sovereign-checklist.md`

**CLAUDE.md Content:**

```markdown
# SovereignSpec Project

This project uses SovereignSpec for Specification-Driven Development.

## Rules
- Read `.sovereignspec/bootstrap.md` before implementing anything
- All specifications are in `.sovereignspec/specs/*.sspec`
- Architecture decisions are in `.sovereignspec/adr/ADR-NNN.md`
- Current tasks are in `.sovereignspec/tasks/active_tasks.md`
- Honor all constraints listed in active specs
- Register artifacts after completing tasks
- Use `/sovereign.*` commands (see .claude/commands/) for the SDD workflow

## Git
- Commit messages follow Conventional Commits
- Spec files are not to be modified by the agent
```

**How Claude Code Discovers Commands:**
Claude Code automatically reads `.claude/commands/*.md` files and recognizes each file as a slash command. The file's name becomes the command name (e.g., `sovereign-constitution.md` becomes `/sovereign.constitution`).

**Command Template Example (`.claude/commands/sovereign-specify.md`):**

```markdown
# /sovereign.specify

Create a new specification for a feature to implement.

## Usage
```
/sovereign.specify <description>
```

## Process
1. Read `.sovereignspec/constitution.md` to understand project principles
2. Read `.sovereignspec/patterns/repository_map.json` to understand the codebase
3. Generate a complete `.sspec` specification file with:
   - A unique kebab-case `id`
   - Clear `purpose` (1-3 sentences)
   - Functional `requirements` (at least 3)
   - Hard `constraints` (at least 2)
   - Testable `acceptance_criteria`
   - Structured `test_cases`
   - `dependencies` ([] if none)
4. Write the spec to `.sovereignspec/specs/{id}.sspec`
5. Validate the spec by running: `sovereignspec spec validate {id}`
6. If validation fails, fix the issues and re-validate

## Output
Return the spec ID and a summary of what the spec defines.
```

**Artifact Submission:**
After completing tasks, Claude Code writes artifacts to `.sovereignspec/agents/claude-code/artifacts.json`.

---

### 3.2 OpenCode

**Files Written:**
- `AGENTS.md`

**AGENTS.md Content:**

```markdown
# SovereignSpec Project

This project uses SovereignSpec for Specification-Driven Development.

## Agent Contract
Read `.sovereignspec/bootstrap.md` for the complete agent contract.

## Available Commands
- `/sovereign.constitution <description>` — Create/update governing principles
- `/sovereign.specify <description>` — Define a new feature spec
- `/sovereign.clarify <spec-id>` — RAG-grounded spec clarification
- `/sovereign.plan <spec-id>` — Generate implementation plan
- `/sovereign.tasks <spec-id>` — Decompose plan into tasks
- `/sovereign.analyze <spec-id>` — Contradiction analysis
- `/sovereign.implement <spec-id>` — Execute implementation
- `/sovereign.checklist <spec-id>` — Generate quality checklist

## Required Reading Order
1. `.sovereignspec/constitution.md`
2. `.sovereignspec/specs/`
3. `.sovereignspec/adr/`
4. `.sovereignspec/tasks/active_tasks.md`
5. `.sovereignspec/patterns/pattern_library.json`

## Artifact Registry
Register completed work at `.sovereignspec/agents/opencode/artifacts.json`.
```

**How OpenCode Discovers SovereignSpec:**
OpenCode reads `AGENTS.md` on project startup and follows its instructions.

---

### 3.3 Cursor

**Files Written:**
- `.cursor/rules/sovereignspec.mdc`

**Rule File Content:**

```markdown
---
description: SovereignSpec Specification-Driven Development rules
globs: ["*.sspec", "**/.sovereignspec/**"]
---

# SovereignSpec Rules

This project uses SovereignSpec. Read `.sovereignspec/bootstrap.md` first.

## Commands
- `/sovereign.constitution` — Create governing principles
- `/sovereign.specify` — Define a new feature spec
- `/sovereign.clarify` — Clarify a spec with RAG
- `/sovereign.plan` — Generate implementation plan
- `/sovereign.tasks` — Break plan into tasks
- `/sovereign.analyze` — Analyze for contradictions
- `/sovereign.implement` — Execute implementation
- `/sovereign.checklist` — Quality checklist

## Contract
Always read specs before coding. Update task status after completion.
Generate tests and docs for every change. Register artifacts.
```

**How Cursor Discovers:**
Cursor automatically applies `.cursor/rules/*.mdc` rules to matching files. When a user opens a `.sspec` file or runs a `/sovereign.*` command, the rules become active.

---

### 3.4 Cline

**Files Written:**
- `.clinerules`

**Content:**

```markdown
# SovereignSpec Project

This project uses SovereignSpec. Read `.sovereignspec/bootstrap.md` for the full contract.

## Custom Commands
- `/sovereign.constitution <description>`: Create/update project constitution at `.sovereignspec/constitution.md`
- `/sovereign.specify <description>`: Create a new `.sspec` spec file in `.sovereignspec/specs/`
- `/sovereign.clarify <spec-id>`: RAG-grounded clarification using ChromaDB and related specs
- `/sovereign.plan <spec-id>`: Generate implementation plan via local LLM with GBNF grammar
- `/sovereign.tasks <spec-id>`: Generate task decomposition as `.sovereignspec/tasks/{id}-tasks.md`
- `/sovereign.analyze <spec-id>`: Cross-spec contradiction and drift analysis
- `/sovereign.implement <spec-id>`: Execute tasks against spec constraints
- `/sovereign.checklist <spec-id>`: Generate quality assurance checklist

## Required Files
Before any implementation, read:
1. `.sovereignspec/constitution.md`
2. `.sovereignspec/specs/` — all `.sspec` files with status `active`
3. `.sovereignspec/adr/ADR-*.md`
4. `.sovereignspec/tasks/active_tasks.md`
5. `.sovereignspec/patterns/pattern_library.json`

## Artifact Submission
Write to `.sovereignspec/agents/cline/artifacts.json`
```

**How Cline Discovers:**
Cline reads `.clinerules` on project startup and applies all rules.

---

### 3.5 RooCode

**Files Written:**
- `.roo/rules.md`

**Content:**

```markdown
# SovereignSpec Mode Configuration

## Role
You are a SovereignSpec SDD agent. You implement features according to specifications.

## Rules
1. Read `.sovereignspec/bootstrap.md` first
2. Read all `.sovereignspec/specs/*.sspec` files before coding
3. Honor all constraints in specs — they are non-negotiable
4. Update task files after completing work
5. Generate tests for every feature
6. Register artifacts
7. Never modify `.sspec` files

## Commands
- `/sovereign.constitution`: Set project principles
- `/sovereign.specify`: Create new spec
- `/sovereign.clarify`: Clarify existing spec
- `/sovereign.plan`: Generate implementation plan
- `/sovereign.tasks`: Decompose into tasks
- `/sovereign.analyze`: Cross-spec analysis
- `/sovereign.implement`: Execute implementation

## Artifacts
Register at `.sovereignspec/agents/roocode/artifacts.json`
```

---

### 3.6 Codex CLI

**Files Written:**
- `AGENTS.md` (global instruction file)
- `skills/sovereign-specify.md` (skills mode)
- `skills/sovereign-plan.md`
- `skills/sovereign-implement.md`

**AGENTS.md Content:**

```markdown
# SovereignSpec Project

This project uses SovereignSpec for specification-driven development.

## Available Skills
- `/sovereign.specify`: Create a new specification
- `/sovereign.plan`: Generate implementation plan
- `/sovereign.implement`: Execute implementation against specs

## Instructions
Read `.sovereignspec/bootstrap.md` first. All specs are in `.sovereignspec/specs/`.
Tasks are in `.sovereignspec/tasks/`. Always read specs before coding.
Register artifacts at `.sovereignspec/agents/codex/artifacts.json`.
```

---

### 3.7 Gemini CLI

**Files Written:**
- `GEMINI.md`

**Content:**

```markdown
# SovereignSpec Project

This project uses SovereignSpec for Specification-Driven Development.

## Project Context
- Specifications: `.sovereignspec/specs/*.sspec`
- Architecture decisions: `.sovereignspec/adr/ADR-*.md`
- Tasks: `.sovereignspec/tasks/active_tasks.md`
- Coding patterns: `.sovereignspec/patterns/pattern_library.json`
- Bootstrap contract: `.sovereignspec/bootstrap.md`

## Workflow
1. Read `.sovereignspec/bootstrap.md` for full contract
2. Read all active specs before implementing
3. After implementation, update task status and register artifacts
4. Create ADR drafts for architectural decisions

## Commands
- `/sovereign.constitution <desc>` — Set principles
- `/sovereign.specify <desc>` — Create spec
- `/sovereign.clarify <id>` — Clarify spec
- `/sovereign.plan <id>` — Plan implementation
- `/sovereign.tasks <id>` — Create tasks
- `/sovereign.implement <id>` — Implement
```

---

### 3.8 Aider

**Files Written:**
- `.aider.conf.yml`

**Content:**

```yaml
# SovereignSpec Aider Configuration
auto-commits: true
lint: true
test: false
watch: false
map-refresh: always
restore-chat-history: true

# System prompt additions
system: |-
  This project uses SovereignSpec for Specification-Driven Development.
  Before making any changes, read `.sovereignspec/bootstrap.md`.
  All specs are in `.sovereignspec/specs/*.sspec`.
  Honor all constraints in spec files. They are non-negotiable.
  After changes, register artifacts at `.sovereignspec/agents/aider/artifacts.json`.
  Create ADR drafts for architectural decisions.
```

---

### 3.9 Windsurf

**Files Written:**
- `.windsurfrules`

**Content:**

```markdown
# SovereignSpec Windsurf Rules

## Project Type
SovereignSpec SDD Project

## Instructions
Read `.sovereignspec/bootstrap.md` before any implementation.
All specifications are `.sspec` files in `.sovereignspec/specs/`.
Architecture decisions are in `.sovereignspec/adr/`.
Tasks are in `.sovereignspec/tasks/`.

## Commands
- /sovereign.constitution — Set governing principles
- /sovereign.specify — Create new specification
- /sovereign.clarify — Clarify specification
- /sovereign.plan — Generate implementation plan
- /sovereign.tasks — Create task list
- /sovereign.analyze — Cross-spec analysis
- /sovereign.implement — Execute implementation

## Contract
Always read specs before coding. Update tasks after completion.
Generate tests. Register artifacts. Never modify .sspec files.
```

---

### 3.10 Continue

**Files Written:**
- `.continue/config.json`
- `.continue/commands/sovereign-specify.md`
- `.continue/commands/sovereign-plan.md`
- `.continue/commands/sovereign-implement.md`

**config.json:**

```json
{
  "experimental": {
    "slashCommands": true
  },
  "slashCommands": [
    {
      "name": "sovereign.specify",
      "description": "Create a new SovereignSpec specification",
      "params": { "description": "Feature description" }
    },
    {
      "name": "sovereign.plan",
      "description": "Generate implementation plan for a spec",
      "params": { "specId": "Spec ID" }
    },
    {
      "name": "sovereign.implement",
      "description": "Execute implementation against a spec",
      "params": { "specId": "Spec ID" }
    }
  ],
  "systemMessage": "This project uses SovereignSpec. Read .sovereignspec/bootstrap.md before implementing."
}
```

---

### 3.11 Generic Filesystem Agent

**Files Written:**
- `.sovereignspec/bootstrap.md` (only — no agent-specific files)

**Fallback Behavior:**
Any file-aware coding agent that reads the project directory discovers `.sovereignspec/bootstrap.md`. The agent reads this file to understand the project structure, the agent contract, and the workflow. No special configuration is needed — the bootstrap.md is self-contained and unambiguous.

---

## 4. /sovereign.* Slash Command Specifications

### `/sovereign.constitution`

**Purpose:** Create or update the project's governing principles (constitution).

**Prompt Template:**
```
You are the SovereignSpec constitution writer for this project.

Read the current state of the project (files, README, any existing code) to understand
what this project does. Then:

1. Generate a `.sovereignspec/constitution.md` file that defines:
   - Project name and purpose
   - Technology stack (languages, frameworks, databases)
   - Architectural principles (e.g., "no ORM", "functional style")
   - Coding standards (naming conventions, file organization)
   - Quality standards (test coverage, documentation requirements)
   - Constraints (what technologies are forbidden)
   - Design philosophy (DDD, clean architecture, etc.)

2. The constitution must be 200-800 words. It serves as the embedding baseline against
   which all future specs are scored for narrative drift.

Output: The full constitution content.
```

### `/sovereign.specify`

**Purpose:** Define a new feature or system to build.

**Prompt Template:**
```
You are the SovereignSpec specification writer.

Read `.sovereignspec/constitution.md` first. Then read any existing specs in
`.sovereignspec/specs/` to understand what's already specified.

Given the description: "{user_description}"

Generate a complete .sspec specification file with all required fields:
- id (kebab-case, unique)
- title 
- version (1.0.0)
- status (draft)
- purpose (1-3 sentences)
- requirements (list, min 3, with action verbs)
- constraints (list, min 2, hard limits only)
- acceptance_criteria (list, min 3, testable pass/fail)
- dependencies (list of existing spec IDs if applicable)
- test_cases (list, min 2, with id/description/given/when/then)
- security_requirements (if applicable)
- implementation_hints

Write the spec to `.sovereignspec/specs/{id}.sspec`.
Return the spec ID and a summary of what it defines.
```

### `/sovereign.clarify`

**Purpose:** RAG-grounded clarification of an existing spec.

**Prompt Template:**
```
You are the SovereignSpec clarification agent.

The user wants to clarify spec "{spec_id}". 

Read the spec at `.sovereignspec/specs/{spec_id}.sspec`.

Then read related specs from `.sovereignspec/specs/` that are linked via
dependencies or that share tags with this spec.

Read relevant ADRs from `.sovereignspec/adr/` that are referenced in this spec.

Read the project constitution from `.sovereignspec/constitution.md`.

The user asks: "{user_question}"

Answer based on the spec content, related specs, ADRs, and constitution.
If the answer is not found in these documents, say so — do not invent information.
```

### `.sovereign/plan`

**Purpose:** Generate a technical implementation plan.

**Prompt Template:**
```
You are the SovereignSpec planning agent.

Read spec `.sovereignspec/specs/{spec_id}.sspec`.

Read the repository map at `.sovereignspec/patterns/repository_map.json`.
Read the pattern library at `.sovereignspec/patterns/pattern_library.json`.

Generate a technical implementation plan with:
1. Architecture overview (how this fits into the existing codebase)
2. File-by-file breakdown of what to create or modify
3. Data model changes (if any)
4. API changes (if any)
5. Testing strategy
6. Implementation order (respecting dependencies)
7. Any migration steps needed

Output format: Markdown with code blocks for file paths.
Write the plan to `.sovereignspec/docs/{spec_id}/implementation.md`.
```

### `/sovereign.tasks`

**Purpose:** Decompose the implementation plan into actionable tasks.

**Prompt Template:**
```
You are the SovereignSpec task decomposition agent.

Read the implementation plan at `.sovereignspec/docs/{spec_id}/implementation.md`.
Read the spec at `.sovereignspec/specs/{spec_id}.sspec`.

Break the implementation into individual tasks. Each task should be:
- A single, completable unit of work
- Associated with specific file paths
- Have clear acceptance criteria
- Be ordered by dependency

Mark tasks that can run in parallel with [P].

Write the tasks to `.sovereignspec/tasks/{spec_id}-tasks.md` using the template format.
```

### `/sovereign.analyze`

**Purpose:** Cross-spec consistency and contradiction analysis.

**Prompt Template:**
```
You are the SovereignSpec analysis agent.

Read the target spec at `.sovereignspec/specs/{spec_id}.sspec`.
Read all active specs in `.sovereignspec/specs/`.
Read the knowledge graph at `.sovereignspec/graph/graph.json`.
Read the constitution at `.sovereignspec/constitution.md`.

Analyze:
1. Contradictions: Does any requirement in this spec conflict with any active spec?
2. Dependency health: Are all dependencies met?
3. Drift score: Does this spec align with the constitution?
4. Completeness: Are there missing fields or underspecified requirements?
5. Impact: What would break if this spec changed?

Output a structured analysis report. Flag any contradictions found.
```

### `/sovereign.implement`

**Purpose:** Execute implementation against spec constraints.

**Prompt Template:**
```
You are the SovereignSpec implementation agent.

Read the spec at `.sovereignspec/specs/{spec_id}.sspec`.
Read the task list at `.sovereignspec/tasks/{spec_id}-tasks.md`.
Read the implementation plan at `.sovereignspec/docs/{spec_id}/implementation.md`.
Read all related specs (dependencies).
Read the pattern library at `.sovereignspec/patterns/pattern_library.json`.
Read the repository map at `.sovereignspec/patterns/repository_map.json`.

Implement all tasks for this spec. For each task:

1. Read the task description and acceptance criteria
2. Implement the code changes
3. Write tests that validate the spec's acceptance criteria
4. Update the task status to [x] completed
5. Register artifacts in `.sovereignspec/agents/{agent_name}/artifacts.json`

After all tasks are complete:
1. Run the tests to verify implementation
2. Update `.sovereignspec/graph/graph.json` with new nodes and edges
3. Create ADR drafts for any architectural decisions made during implementation
4. Generate documentation for any new modules

Constraints to never violate:
- {spec constraints from the spec file}
- Do not modify .sspec files
- Do not add dependencies not listed in specs
- Do not use cloud APIs
```

### `/sovereign.checklist`

**Purpose:** Generate a quality checklist for a spec.

**Prompt Template:**
```
You are the SovereignSpec quality assurance agent.

Read the spec at `.sovereignspec/specs/{spec_id}.sspec`.
Read any implemented code related to this spec.
Read the tests for this spec.

Generate a quality checklist covering:
1. Are all requirements implemented? (check each against code)
2. Are all constraints honored? (verify no violations)
3. Do all acceptance criteria pass? (check test results)
4. Is there test coverage for each acceptance criterion?
5. Is documentation complete?
6. Are there any security concerns?
7. Are there any performance concerns?
8. Is the knowledge graph up to date?
9. Are all artifacts registered?
10. Is the spec status correct?

Output: Checklist with [PASS]/[FAIL] for each item.
```

---

## 5. Context Package Format (agent_context.md)

The context package is assembled by `sovereignspec context build <spec-id>` and written to `agent_context/{spec-id}-context.md`.

**Structure:**

```markdown
# Agent Context: {spec-id}
Generated: {timestamp}
Target Agent: {adapter-name}

## 1. Current Specification
Full content of `.sovereignspec/specs/{spec-id}.sspec`:
---
{paste spec content}
---

## 2. Related Specifications (Top 5 by Graph Proximity)
### {related-spec-1}
Paste of related spec content (abbreviated)
### {related-spec-2}
...

## 3. Relevant Architecture Decision Records
### ADR-{NNN}: {title}
Summary: {rationale}
...

## 4. Repository Coding Patterns (Top 10)
{pattern entries from pattern_library.json}

## 5. Knowledge Graph Context
### Dependency Chain
{spec} → {dep1} → {dep2}
### What Breaks If This Spec Changes
{affected nodes}

## 6. Active Tasks
{task list for this spec}

## 7. Previous Implementation Artifacts
{artifacts from previous sessions for this spec}
```

---

## 6. Artifact Submission Protocol

**File:** `.sovereignspec/agents/{agent-name}/artifacts.json`

**Schema:**
```json
{
  "$schema": "sovereignspec-artifact-registry",
  "agent": "claude-code",
  "project": "my-project",
  "artifacts": [
    {
      "id": "uuid-string",
      "task_id": "uuid-string",
      "artifact_type": "code",
      "file_path": "src/auth/jwt.ts",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z",
      "spec_id": "jwt-authentication",
      "checksum": "sha256-hex-string"
    }
  ]
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | string | Always "sovereignspec-artifact-registry" |
| `agent` | string | Agent name (e.g., "claude-code", "opencode") |
| `project` | string | Project slug |
| `artifacts[]` | array | List of artifact records |
| `artifacts[].id` | string | UUID v4 |
| `artifacts[].task_id` | string | UUID of the task that produced this artifact |
| `artifacts[].artifact_type` | string | One of: "code", "test", "doc", "config", "migration", "other" |
| `artifacts[].file_path` | string | Path relative to project root |
| `artifacts[].validated` | boolean | Whether artifact has passed validation against spec acceptance criteria |
| `artifacts[].created_at` | string | ISO 8601 timestamp |
| `artifacts[].spec_id` | string | (optional) Spec ID this artifact relates to |
| `artifacts[].checksum` | string | (optional) SHA-256 of file content |

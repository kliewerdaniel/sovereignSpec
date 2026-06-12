# SovereignSpec Project Contract

## What is SovereignSpec?

SovereignSpec is a local-first, fully offline Spec-Driven Development (SDD) engine. This project uses SovereignSpec to manage its specifications, architecture decisions, tasks, and knowledge graph. All specifications are in `.sspec` files. All implementation is driven by these specifications.

The core thesis is: **Human → Specification → SovereignSpec → Agent → Implementation**. The specification is the durable artifact. The code is disposable. The spec is alive. The code obeys. Nothing leaves your machine.

## Your Role

You are a coding agent working within this SovereignSpec project. Your task is to read the project's specifications, understand the requirements and constraints, and implement code that satisfies the acceptance criteria. The specification is the source of truth — the code is downstream and disposable.

You do not need prior knowledge of SovereignSpec. This file contains everything you need to understand the project structure, your responsibilities, and the workflow.

## Required Reading (in order)

Before implementing anything, read these files in order:

1. **`.sovereignspec/constitution.md`** — Project governing principles. This defines the technology stack, architectural style, coding standards, and non-negotiable constraints. Every spec is scored against this constitution for narrative drift.

2. **`.sovereignspec/specs/`** — All `.sspec` specification files. Each file defines a feature or system to build, including requirements, constraints, acceptance criteria, and test cases. Start with specs whose `status` is `active`.

3. **`.sovereignspec/adr/`** — Architecture Decision Records. These explain why architectural choices were made. Read them before making architectural decisions yourself.

4. **`.sovereignspec/tasks/active_tasks.md`** — Current work units. This file lists pending, in-progress, and completed tasks organized by spec.

5. **`.sovereignspec/patterns/pattern_library.json`** — Coding conventions extracted from the existing codebase. Follow these patterns when writing new code.

6. **`.sovereignspec/patterns/repository_map.json`** — Repository structure map showing modules, entrypoints, and dependencies.

## The Agent Contract

For every task you work on, you must:

### 1. Read Specifications Before Writing Any Code

Always start by reading the relevant `.sspec` file(s) in `.sovereignspec/specs/`. Understand:
- The purpose (why this feature exists)
- All functional requirements (what it must do)
- All constraints (hard limits that cannot be violated)
- The acceptance criteria (how correct implementation is verified)
- The test cases (what tests must pass)

### 2. Update Task Status Upon Completion

After completing a task, update the task list file at `.sovereignspec/tasks/{spec-id}-tasks.md`:
- Change `[ ] pending` to `[x] completed` for the completed task
- Add a completion note under the task: `Completed: YYYY-MM-DD — Brief summary of what was done`

### 3. Generate Tests for Every Implemented Feature

For every feature you implement, generate tests that validate the spec's acceptance criteria. Test files should be:
- Placed according to the project's test conventions (see `pattern_library.json`)
- Covering all acceptance criteria in the spec
- Covering edge cases (empty input, invalid input, boundary conditions)
- Covering error conditions (401, 403, 404, 429, 500 responses)

### 4. Generate Documentation for Every Module Changed

For every module you create or modify, generate documentation that explains:
- What the module does
- Its public API (exports, functions, classes)
- Usage examples
- Any configuration required

### 5. Honor All Constraints Listed in Active Specs

Constraints in `.sspec` files are non-negotiable. They define hard limits that cannot be violated. If a constraint says "No ORM," do not introduce an ORM. If a constraint says "No cloud APIs," do not call any external API.

### 6. Update the Knowledge Graph After Implementation

After completing implementation, update `.sovereignspec/graph/graph.json`:
1. Add a node for each new module or endpoint you created (use `id: "mod-{path}"` format)
2. Add `REFERENCES` edges from the spec node to new module/endpoint nodes
3. Add `GENERATES` edges from the spec to any new documentation files
4. If you created a new ADR, add a `REFERENCES` edge from the spec to the ADR

### 7. Record All New Architectural Decisions as ADR Drafts

If your implementation reveals a significant architectural decision not covered by existing ADRs:
1. Find the next ADR number (check existing files in `.sovereignspec/adr/`)
2. Create `.sovereignspec/adr/ADR-NNN.md` using the ADR template
3. The ADR must include: context, decision, rationale, alternatives considered, and consequences

### 8. Register Artifacts

After completing all tasks for a spec, register every generated file in the artifact registry at:

`.sovereignspec/agents/{your-agent-name}/artifacts.json`

The format is:
```json
{
  "agent": "your-agent-name",
  "artifacts": [
    {
      "id": "uuid-v4",
      "task_id": "task-uuid",
      "artifact_type": "code|test|doc|config|migration",
      "file_path": "src/auth/jwt.ts",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

## Specification Format Quick Reference

`.sspec` files use a YAML superset format with these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | kebab-case unique identifier |
| `title` | string | yes | human-readable title |
| `version` | semver | yes | e.g. "1.0.0" |
| `status` | enum | yes | draft, validated, approved, active, implemented, verified, archived |
| `purpose` | string | yes | 1-3 sentence description |
| `requirements` | [string] | yes | functional requirements (min 1) |
| `constraints` | [string] | yes | hard limits (min 1) |
| `acceptance_criteria` | [string] | yes | testable pass/fail criteria (min 1) |
| `dependencies` | [string] | yes | spec IDs this depends on (can be `[]`) |
| `test_cases` | [object] | yes | structured test definitions (min 1) |
| `security_requirements` | [string] | no | security controls |
| `performance_requirements` | [object] | no | performance targets |
| `architecture_notes` | string | no | architectural guidance |
| `implementation_hints` | [string] | no | implementation guidance |
| `tags` | [string] | no | categorization tags |

### Test Case Format

Each test case has:
```yaml
- id: PREFIX-NNN
  description: What is being tested
  given: Preconditions
  when: Action to take
  then: Expected outcome
```

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

- `[P]` marks tasks that can run in parallel with their siblings
- Tasks with dependencies list them in parentheses
- Each task specifies exact file paths
- Each task has an acceptance criterion

## Artifact Submission

After completing implementation for a spec, register artifacts at:

`.sovereignspec/agents/{agent-name}/artifacts.json`

```json
{
  "agent": "claude-code",
  "artifacts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "artifact_type": "code",
      "file_path": "src/auth/login.ts",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Artifact types:** `code`, `test`, `doc`, `config`, `migration`, `other`

## ADR Creation

When you make an architectural decision not covered by existing ADRs:

1. Find the next available ADR number (highest number in `.sovereignspec/adr/ADR-*.md` + 1)
2. Create `.sovereignspec/adr/ADR-NNN.md`:

```markdown
# ADR-NNN: Title
Status: proposed
Date: YYYY-MM-DD

## Context
Why this decision was needed. What problem is being solved.

## Decision
What was decided. The architecture change or new pattern adopted.

## Rationale
Why this option was chosen over alternatives.

## Alternatives Considered
Other options that were evaluated and why they were rejected.

## Consequences
Positive and negative effects of this decision.
```

## Constraints You Must Never Violate

These are universal constraints that apply to every task in this project:

1. **Do not modify `.sspec` files.** Specs are upstream artifacts authored by the project maintainer. You may create new specs via `/sovereign.specify` but never modify existing ones.
2. **Do not delete Architecture Decision Records.** ADRs are permanent records of architectural decisions.
3. **Do not modify `graph.json` node definitions without creating corresponding edges.** Every new node must be connected via at least one edge.
4. **Do not implement features that are not specified in an active `.sspec` file.** Code must trace back to a spec's requirements and acceptance criteria.
5. **Do not use external APIs or cloud services.** This is a local-first project. No inference, storage, or processing should leave the local machine.
6. **Do not introduce dependencies not listed or implied by the specs.** If a spec constrains the tech stack, honor it.
7. **All secrets, keys, and tokens must be environment-variable configured.** Never hardcode credentials, API keys, or tokens in source code.
8. **Do not skip tests.** Every feature must have corresponding tests that validate the spec's acceptance criteria.
9. **Do not leave TODO comments or stubs in implementation code.** If a feature is incomplete, update the task status and create a new task for the remaining work.

## Knowledge Graph Structure

File: `.sovereignspec/graph/graph.json`

The graph stores nodes and edges in adjacency list format:

```json
{
  "nodes": [
    {"id": "spec-jwt-authentication", "type": "Specification", "metadata": {...}},
    {"id": "mod-src-auth", "type": "Module", "metadata": {...}}
  ],
  "edges": [
    {"source": "spec-jwt-authentication", "target": "mod-src-auth", "type": "REFERENCES", "weight": 1.0}
  ]
}
```

### Node Types
- `Project` — The SovereignSpec project itself
- `Feature` — A user-facing feature
- `Specification` — A `.sspec` file
- `Module` — A source code module
- `Service` — A deployable service/component
- `Endpoint` — An API endpoint
- `Database` — A database or table
- `ADR` — An Architecture Decision Record
- `Task` — An implementation task
- `Agent` — A coding agent session
- `Document` — A generated documentation file

### Edge Types
- `IMPLEMENTS` — Task implements Specification
- `DEPENDS_ON` — Spec A depends on Spec B
- `REFERENCES` — Spec refers to ADR or Module
- `GENERATES` — Spec generated a Document
- `REPLACES` — New spec replaces old spec
- `SUPERSEDES` — New ADR supersedes old ADR
- `CONFLICTS_WITH` — Specs have contradictory requirements
- `RELATED_TO` — Specs share context
- `VALIDATES` — Test validates Specification

### Node ID Conventions
- Spec: `spec-{spec-id}`
- Module: `mod-{path-slug}`
- Endpoint: `ep-{method}-{path-slug}`
- ADR: `adr-{NNN}`
- Feature: `feat-{kebab-name}`
- Task: `task-{uuid}`
- Agent: `agt-{name}`
- Database: `db-{table-name}`
- Document: `doc-{path-slug}`
- Service: `svc-{name}`

## Working with This Project

### Understanding the Workflow

The SovereignSpec workflow follows this pipeline:

```
/sovereign.constitution → /sovereign.specify → /sovereign.clarify
→ /sovereign.plan → /sovereign.tasks → /sovereign.analyze
→ /sovereign.implement → /sovereign.checklist
```

Each command feeds into the next. The constitution grounds everything. Specs emerge from the constitution. Plans emerge from specs. Tasks emerge from plans. Implementation executes tasks. Analysis checks consistency. The checklist verifies quality.

### Proceeding Without Supervisor

If you can operate autonomously (no human-in-the-loop required), follow this process for each spec:

1. Read the spec and all related specs
2. Check for existing implementation (any artifacts in the registry?)
3. If implementing: read each task, implement the code, test it, document it, register the artifact
4. If the spec introduces new architectural decisions, create an ADR draft
5. Update the knowledge graph with new nodes and edges
6. Update task statuses as you complete work
7. Provide a summary of what was implemented, what was tested, and any decisions made

### Communication Style

When reporting progress, be concise and structured:
- **What was implemented**: List files created/modified
- **What was tested**: List test files and coverage
- **What was decided**: Any ADRs created or architectural decisions made
- **What remains**: Any blocked tasks or pending work
- **Blockers**: Any issues that need human intervention

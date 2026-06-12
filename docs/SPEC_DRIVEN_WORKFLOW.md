# SovereignSpec Spec-Driven Workflow

**Version 1.0.0 — Complete Workflow Guide**

---

## 1. SDD Concepts (For New Users)

### The Context Hierarchy

SovereignSpec organizes context into five layers, from broadest to most specific:

1. **Global Rules** — `.sovereignspec/bootstrap.md` and `.sovereignspec/constitution.md`. These define what this project is, what technologies it uses, and the non-negotiable rules every agent must follow.

2. **Architecture Decisions** — `.sovereignspec/adr/ADR-NNN.md` files. These record why architectural choices were made. They provide context for why things are structured the way they are.

3. **Specifications** — `.sovereignspec/specs/*.sspec` files. These define what to build. Each spec is a complete, structured definition of a feature or system with requirements, constraints, and acceptance criteria.

4. **Repository Patterns** — `.sovereignspec/patterns/pattern_library.json` and `.sovereignspec/patterns/repository_map.json`. These describe how the existing codebase is structured — naming conventions, error handling patterns, file organization.

5. **Task Context** — `.sovereignspec/tasks/{spec-id}-tasks.md`. These decompose a spec into individual, completable work units with file paths and acceptance criteria.

### Functional vs Technical Specs

**Functional specs** describe what the system does from a user's perspective. They define features, endpoints, behaviors, and outcomes. Example: "Users must authenticate with email and password."

**Technical specs** describe how the system implements the functional requirements. They define data models, algorithms, middleware chains, and deployment topology. Example: "Tokens must be stateless (no server-side session store)."

In SovereignSpec, most `.sspec` files are functional specs. Technical details belong in the `architecture_notes`, `constraints`, and `implementation_hints` fields. Pure technical specs (like "Database Migration Workflow") are valid but should be the exception.

### Specs as Upstream Artifacts

Code is downstream of specs. When you find a bug, you do not fix the code directly — you fix the spec and regenerate. When the spec and code disagree, the spec wins. This means:

- **Specs are authoritative**: All code exists to satisfy specs
- **Code is disposable**: Regenerate from spec when the spec changes
- **Tests validate specs**, not code

### The SDD Artifact Stack

Working from spec to implementation, the artifacts are:

```
Constitution (governing principles)
  → Specification (.sspec, what to build)
    → Implementation Plan (how to build it)
      → Task List (individual work units)
        → Implementation (code + tests + docs)
          → Artifacts (registered outputs)
            → Updated Knowledge Graph (edges from new nodes)
```

---

## 2. Complete Walkthrough — Building a REST API from Zero to Implementation

### Phase 1: Initialize Project and Establish Constitution

```bash
# Create the project
sovereignspec init my-api --adapter claude-code
cd my-api

# Establish governing principles
sovereignspec sovereign-constitution \
  "Build a REST API with TypeScript, Express, and SQLite. \
   No ORM. Use raw SQL via better-sqlite3. \
   Functional programming style with pure functions and immutable data. \
   All secrets environment-variable configured. \
   100% test coverage for all endpoints."
```

**What happens:**
- `.sovereignspec/` directory tree created
- `constitution.md` generated and embedded for drift scoring baseline
- Claude Code integration files written (CLAUDE.md + .claude/commands/*.md)

### Phase 2: Write the First Specification

```bash
# Using the agent command
# /sovereign.specify "User registration and authentication with JWT tokens"

# Or using the CLI directly
sovereignspec spec create user-auth \
  --title "User Authentication" \
  --purpose "Provide user registration and JWT-based authentication"
```

This creates `specs/user-auth.sspec` with the template. Edit it:

```yaml
id: user-auth
title: User Authentication
version: 1.0.0
status: draft
purpose: Provide user registration and JWT-based authentication with email and password.

requirements:
  - Users can register with email and password
  - Registered users can log in to receive JWT tokens
  - Tokens expire after 24 hours
  - Authenticated users can access protected routes

constraints:
  - No third-party auth providers
  - Passwords hashed with bcrypt
  - SQLite only

acceptance_criteria:
  - POST /auth/register creates user and returns 201
  - POST /auth/login with valid credentials returns 200 + token
  - GET /auth/me with valid token returns user profile

dependencies: []

test_cases:
  - id: AUTH-001
    description: User registration succeeds
    given: Valid email and password
    when: POST /auth/register
    then: Response 201 with user ID
```

### Phase 3: Clarify the Spec

```bash
# Run in agent:
# /sovereign.clarify user-auth

# Or CLI:
sovereignspec clarify user-auth
```

The agent will RAG-retrieve related specs, ADRs, and patterns, then enter an interactive Q&A session. This is where ambiguities are resolved before generating code.

### Phase 4: Generate Implementation Plan

```bash
# /sovereign.plan user-auth
# or
sovereignspec plan user-auth --tech-stack "TypeScript, Express, SQLite"
```

The LLM (constrained by `implementation_plan.gbnf`) generates:

**Output:** `docs/user-auth/implementation.md` with:
- Architecture overview
- File-by-file breakdown
- Data model changes
- Implementation order

### Phase 5: Break into Tasks

```bash
# /sovereign.tasks user-auth
# or
sovereignspec tasks user-auth
```

**Output:** `tasks/user-auth-tasks.md`:

```markdown
# Tasks: user-auth v1.0.0

## [P] Task 1: User Registration Endpoint
Create POST /auth/register handler
Status: [ ] pending
Files: src/routes/auth.ts, src/services/user-service.ts
Acceptance: POST /auth/register returns 201 and creates user in database

## [P] Task 2: Password Hashing Utility
Create bcrypt-based password hashing
Status: [ ] pending
Files: src/utils/password.ts
Acceptance: Hash and verify passwords correctly

## Task 3: Login Endpoint (depends on 1, 2)
Create POST /auth/login with JWT generation
Status: [ ] pending
Files: src/routes/auth.ts, src/utils/jwt.ts
Acceptance: POST /auth/login returns JWT token

## Task 4: Auth Middleware (depends on 3)
Create JWT verification middleware
Status: [ ] pending
Files: src/middleware/auth.ts
Acceptance: Protected routes return 401 without valid token
```

### Phase 6: Analyze for Consistency

```bash
# /sovereign.analyze user-auth
# or
sovereignspec analyze user-auth
```

The analyzer checks:
- **Contradictions**: Does any requirement conflict with other active specs?
- **Dependency health**: Are all dependencies met? (None in this case)
- **Drift score**: Does this align with the constitution? (Score: 0.85 — good)
- **Completeness**: Are any fields missing or underspecified?

### Phase 7: Implement

```bash
# /sovereign.implement user-auth
# or
sovereignspec implement user-auth
```

The agent context package is assembled and the agent executes each task:
1. Reads the spec and each task's acceptance criteria
2. Implements code files
3. Writes tests
4. Updates task status
5. Registers artifacts

### Phase 8: Verify Implementation

After implementation, verify against acceptance criteria:

```bash
# Run the generated tests
npm test

# Check artifact registry
cat .sovereignspec/agents/claude-code/artifacts.json
```

Each artifact's `validated` field shows whether it passed validation against the spec's acceptance criteria. Run `sovereignspec spec validate user-auth` to re-check the spec and ensure implementation satisfies all requirements.

### Phase 9: Archive Spec

When the spec is fully implemented and verified:

```bash
sovereignspec spec compile user-auth  # Updates version
# Set status to verified after manual review
# (edit .sspec file: status: verified)
# Then archive:
# (edit .sspec file: status: archived)
```

---

## 3. Working with Multiple Specs

### Dependency Management

Specs declare dependencies via the `dependencies[]` field. The compiler resolves these into a directed graph and enforces implementation order.

**Example:**
```yaml
# specs/rate-limiting.sspec
id: rate-limiting
dependencies:
  - user-auth  # Must have auth before we can rate-limit it

# specs/api-gateway.sspec
id: api-gateway
dependencies:
  - user-auth        # Auth first
  - rate-limiting    # Then rate limiting
  - user-profile-api # Then user profiles
```

The compiler performs topological sort to determine compilation and implementation order. Circular dependencies are detected and rejected.

### Parallel Specs

Specs without dependency chains can be worked on in parallel:

```bash
# These specs have no dependencies on each other
sovereignspec implement email-notifications &
sovereignspec implement avatar-upload &
```

The knowledge graph tracks both implementations. When they both reference the same module, the graph will show both specs with REFERENCES edges to that module.

---

## 4. Spec Evolution

### Updating a Spec

```bash
# Edit the spec file
# Change requirements, add constraints, etc.

# Re-compile to generate new version
sovereignspec spec compile user-auth
```

This creates a new version in `spec_versions`. The diff is computed and stored. Previous versions remain accessible.

### Rolling Back

```bash
sovereignspec spec compile user-auth --rollback
```

This reverts to the previous version record. The graph and embeddings are also rolled back.

### Superseding a Spec

When a spec is completely replaced:

```yaml
# specs/user-auth-v2.sspec
id: user-auth-v2
dependencies:
  - user-auth  # Will SUPERSEDE this
```

Compile with:
```bash
sovereignspec spec compile user-auth-v2 --supersedes user-auth
```

This creates a `SUPERSEDES` edge in the knowledge graph and archives the old spec.

---

## 5. Contradiction Resolution Workflow

When `sovereignspec analyze --all` flags a contradiction:

### Step 1: Understand the Conflict

```bash
sovereignspec analyze user-auth
# Output:
# ✗ rate-limiting: CONFLICT (score: 0.82)
#   "user-auth specifies 24-hour token expiry, rate-limiting specifies
#    15-minute token expiry on auth endpoints"
```

### Step 2: Resolve via Spec Update

Edit one of the conflicting specs to resolve the contradiction. The contradiction detection uses embedding similarity — update the requirement text to be consistent.

### Step 3: Re-analyze

```bash
sovereignspec analyze user-auth
# Output:
# ✓ rate-limiting: No contradiction (resolved)
```

### Step 4: If Unresolvable

If the contradiction is legitimate (two features genuinely conflict), create an ADR documenting the conflict and the decision on which spec takes precedence:

```bash
sovereignspec adr create \
  --title "Token Expiry Conflict Resolution" \
  --context "user-auth and rate-limiting specs have contradictory token expiry requirements"
```

---

## 6. Narrative Drift Remediation

When a spec has a drift score below 0.6:

### Step 1: Identify the Drift

```bash
sovereignspec analyze user-auth
# Output:
# ✓ Drift score: 0.72 (threshold: 0.6) -- OK
#
# If score < 0.6:
# ✗ NARRATIVE_DRIFT: Spec has drifted from constitution
#   Constitution says: "No ORM. Use raw SQL."
#   Spec requires: "Use Prisma ORM for database access"
```

### Step 2: Realign

Update the spec to align with the constitution. If the constitution is wrong (the project's direction has legitimately changed), update the constitution instead:

```bash
sovereignspec sovereign-constitution \
  "Build a REST API with TypeScript, Express, SQLite, and Prisma ORM."
```

### Step 3: Re-check

```bash
sovereignspec analyze user-auth
# Score should now be above 0.6
```

---

## 7. ADR Workflow

ADRs are created when a significant architectural decision is made:

### When to Create an ADR

- Choosing a database technology
- Adopting a framework or library
- Deciding on an architectural pattern (microservices, event-driven, etc.)
- Resolving a spec contradiction
- Changing a constraint that affects multiple specs

### ADR Creation

```bash
sovereignspec adr create \
  --title "Use better-sqlite3 for Database Access" \
  --context "Need local SQLite with synchronous API"
```

### ADR Lifecycle

1. **Proposed**: Created via `sovereignspec adr create`
2. **Accepted**: Approved after review (update status in ADR file)
3. **Deprecated**: No longer relevant
4. **Superseded**: Replaced by a newer ADR

### Linking ADRs to Specs

Specs reference ADRs via the `related_adrs` field:

```yaml
# In .sspec file
related_adrs:
  - ADR-004
```

The compiler creates `REFERENCES` edges from the ADR node to the spec node in the knowledge graph.

---

## 8. Multi-Agent Workflow

SovereignSpec supports multiple agents working on the same project simultaneously:

### Setup

```bash
# Register both agents
sovereignspec integrate --agent claude-code
sovereignspec integrate --agent opencode

# Assign different specs to different agents
sovereignspec tasks user-auth        # Claude Code works on this
sovereignspec tasks rate-limiting    # OpenCode works on this
```

### Coordination via Knowledge Graph

Both agents read and write to the same `graph.json`. The graph becomes the coordination mechanism:
- Agent A completes a task → adds edges from modules to the spec
- Agent B sees those edges when it reads the graph → knows which modules exist
- If both agents modify the same module, the graph will show two incoming REFERENCES edges

### Conflict Prevention

- Assign independent specs (no shared DEPENDS_ON chain) to different agents
- Use `sovereignspec analyze --all` regularly to detect cross-agent contradictions
- Run `sovereignspec memory sync` before each agent session to ensure up-to-date graph

---

## 9. Common Patterns

### Authentication Spec Pattern

Every auth-related spec should include:
- `security_requirements` for password policies, token algorithms
- `performance_requirements` for login throughput
- Rate limiting as a constraint
- Test cases covering: success, invalid credentials, expired tokens, missing tokens, rate limiting

### CRUD API Spec Pattern

Every CRUD spec should include:
- Requirements for all four operations (or a subset if read-only)
- Pagination for list operations
- Input validation requirements
- Authorization (who can do what)
- Test cases for: success, not found, unauthorized, validation error, duplicate creation

### Event System Spec Pattern

Every event system spec should include:
- Event schema definition
- Publishing requirements (sync vs async)
- Subscription requirements (filter, transform)
- Delivery guarantees (at-least-once, exactly-once)
- Error handling (dead letter queue, retry policy)

### Background Job Spec Pattern

Every background job spec should include:
- Job definition (what work is done)
- Scheduling (cron, interval, triggered)
- Concurrency limits
- Error handling (retry, backoff, failure notification)
- Monitoring (progress tracking, logging)

---

## 10. Anti-Patterns to Avoid

### 1. Specs That Are Too Large

**Problem:** A single spec with 50+ requirements becomes unwieldy. The compiler generates too many tasks. The knowledge graph has a single node with too many edges.

**Solution:** Split into multiple focused specs. A spec should define one feature or system, not an entire application.

### 2. Specs That Repeat Constitution Rules

**Problem:** Every spec repeats "No cloud APIs" instead of relying on the constitution.

**Solution:** Include global constraints in the constitution. Specs only need spec-specific constraints. The compiler includes the constitution in every context package.

### 3. Circular Dependencies

**Problem:** Spec A depends on Spec B, which depends on Spec A.

**Solution:** The compiler detects and rejects these. Restructure to remove the cycle — often by extracting shared functionality into a third spec.

### 4. Ignoring the Knowledge Graph

**Problem:** Implementors modify code without updating `graph.json`.

**Solution:** The artifact submission protocol requires graph updates. Run `sovereignspec memory sync --rebuild-graph` periodically to recover.

### 5. Over-Specifying Implementation Details

**Problem:** Specs dictate exact library versions, file names, and line counts.

**Solution:** Keep specs at the "what" level. The "how" belongs in `implementation_hints` and `architecture_notes`, which are advisory, not required.

### 6. Specs Without Test Cases

**Problem:** Specs define requirements and acceptance criteria but skip `test_cases`.

**Solution:** The `MISSING_TEST_CASES` validation rule prevents compilation of specs without test cases. Always include at least one test case per requirement.

### 7. Editing .sspec Files Directly Instead of Using /sovereign.specify

**Problem:** Hand-editing `.sspec` files bypasses validation and version tracking.

**Solution:** Use the agent's `/sovereign.specify` command or the CLI's `sovereignspec spec create` to generate valid specs. Manual edits are allowed but must be followed by `sovereignspec spec validate`.

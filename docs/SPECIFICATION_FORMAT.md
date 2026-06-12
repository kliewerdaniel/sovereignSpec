# SovereignSpec Specification Format (.sspec)

**Version 1.0.0 — Complete Format Reference**

---

## 1. Philosophy: Why .sspec Instead of Plain Markdown

Plain markdown specifications are human-readable but machine-opaque. They cannot be:
- **Validated programmatically**: No field-level type checking, required fields, or constraint enforcement
- **Compiled deterministically**: Free-form text requires the LLM to infer structure, introducing variance
- **Versioned with semantic awareness**: Git diff on markdown is line-level, not field-level
- **Graph-integrated**: No typed relationships between spec fields and knowledge graph nodes
- **Grammar-constrained**: GBNF grammars require typed output schemas that map to structured input

The `.sspec` format solves all five problems. It is a YAML superset with required typed fields, validation rules, and a defined lifecycle. Every field has a purpose, a validation rule, and a compiler behavior. This makes specs machine-readable, compiler-processable, and deterministic.

---

## 2. Complete .sspec Field Reference

### Required Fields

#### `id`
- **Type**: string
- **Required**: Yes
- **Description**: Unique identifier for the spec. Must be kebab-case (lowercase letters, numbers, and hyphens). Immutable after first commit — changing the ID orphans the spec in the knowledge graph.
- **Valid Values**: `/^[a-z0-9]+(-[a-z0-9]+)*$/`
- **Example**: `jwt-authentication`
- **Validation**: Must not collide with any existing spec ID in the project. Must match the kebab-case pattern.
- **Compiler Effect**: Used as the graph node ID prefix (`spec-{id}`). Used as the filename (`specs/{id}.sspec`).

#### `title`
- **Type**: string
- **Required**: Yes
- **Description**: Human-readable spec title, 5-60 characters. Used in CLI output, UI, and documentation headers.
- **Example**: `JWT Authentication System`
- **Validation**: Must be non-empty. Max 120 characters.
- **Compiler Effect**: Used as document title in generated docs. Used as node label in knowledge graph.

#### `version`
- **Type**: string (semver)
- **Required**: Yes
- **Description**: Spec version following semantic versioning. Major = breaking requirement changes, Minor = non-breaking additions, Patch = clarifications and fixes.
- **Valid Values**: `/^\d+\.\d+\.\d+$/`
- **Example**: `1.0.0`
- **Validation**: Must be valid semver. Must be >= previous version on update.
- **Compiler Effect**: Recorded in SQLite `spec_versions`. Used for diff tracking.

#### `status`
- **Type**: enum
- **Required**: Yes
- **Description**: Current lifecycle state of the spec. Determines which operations are allowed.
- **Valid Values**: `draft | validated | approved | active | implemented | verified | archived`
- **Example**: `draft`
- **Validation**: Must be a valid lifecycle state. Transitions must follow the state machine rules (see Section 6.4 of ARCHITECTURE.md).
- **Compiler Effect**: Affects whether the spec is included in agent context. Only `active` specs generate tasks.

#### `purpose`
- **Type**: string
- **Required**: Yes
- **Description**: 1-3 sentence description of what this specification accomplishes and why it exists. Answers the question "Why are we building this?"
- **Example**: `Provide secure JWT-based authentication with access and refresh token flows, supporting role-based access control for admin, user, and viewer roles.`
- **Validation**: Must be 50-500 characters. Must contain a verb describing the action. Must not be a copy of `title`.
- **Compiler Effect**: Used as the primary context for LLM prompts. Embedded in ChromaDB for semantic search.

#### `requirements`
- **Type**: list of strings
- **Required**: Yes (minimum 1)
- **Description**: Functional requirements that the implementation must satisfy. Each requirement must contain an action verb and a measurable outcome.
- **Format**: Each item: `"System must [action] [object] [condition]."`
- **Example**:
  ```yaml
  requirements:
    - Users must authenticate with email and password
    - System issues short-lived access tokens (15 min) and long-lived refresh tokens (7 days)
    - Refresh tokens are single-use and rotated on each refresh
  ```
- **Validation**: Min 1 item. Each item must contain an action verb. No duplicate requirements.
- **Compiler Effect**: Each requirement generates at least one task during compilation. Each requirement is embedded separately for semantic search.

#### `constraints`
- **Type**: list of strings
- **Required**: Yes (minimum 1)
- **Description**: Hard limits that the implementation must respect. These are non-negotiable rules that cannot be violated.
- **Example**:
  ```yaml
  constraints:
    - No third-party auth providers (Google, GitHub OAuth)
    - Tokens must be stateless (no server-side session store)
    - All secrets must be environment-variable configured
  ```
- **Validation**: Min 1 item. Each item must describe a limit or restriction. No contradictions with existing spec constraints.
- **Compiler Effect**: Included in every agent context package as "must not violate" rules. GBNF grammars use constraints to filter generated code patterns.

#### `acceptance_criteria`
- **Type**: list of strings
- **Required**: Yes (minimum 1)
- **Description**: Testable pass/fail criteria. Each criterion must be objectively verifiable (yes/no, pass/fail). These define when the implementation is complete.
- **Format**: `[HTTP method/action] [endpoint/component] [condition] [expected result]`
- **Example**:
  ```yaml
  acceptance_criteria:
    - POST /auth/login returns { access_token, refresh_token }
    - POST /auth/refresh with valid refresh token returns new token pair
    - POST /auth/refresh with expired token returns 401
    - GET /protected without token returns 401
  ```
- **Validation**: Min 1 item. Each item must be testable (no subjective criteria). No overlapping criteria.
- **Compiler Effect**: Generates test cases in the test plan. Used for artifact validation.

#### `dependencies`
- **Type**: list of strings
- **Required**: Yes (can be empty `[]`)
- **Description**: List of spec IDs that this spec depends on. The dependent spec must be at minimum in `validated` status before this spec can become `active`.
- **Example**: `[user-profile-api]` (meaning this spec depends on the user-profile-api spec)
- **Validation**: Each dependency must be a known spec ID (must exist in project). No circular dependencies.
- **Compiler Effect**: Creates `DEPENDS_ON` edges in the knowledge graph. Determines compilation order.

#### `test_cases`
- **Type**: list of objects
- **Required**: Yes (minimum 1)
- **Description**: Structured test cases that define expected behavior. Each test case has five fields.
- **Fields**:
  - `id` (string, required): Unique test ID within this spec. Use prefix convention: `{SPEC-ABBREV}-{NNN}`.
  - `description` (string, required): What is being tested, in one sentence.
  - `given` (string, required): Preconditions that must be set up before the test.
  - `when` (string, required): The action being taken.
  - `then` (string, required): Expected outcome.
- **Example**:
  ```yaml
  test_cases:
    - id: AUTH-001
      description: Successful login returns tokens
      given: Valid registered user credentials
      when: POST /auth/login with valid email and password
      then: Response status 200 with access_token and refresh_token
  ```
- **Validation**: Min 1 item. Each item must have all five fields non-empty. Test IDs must be unique within the spec.
- **Compiler Effect**: Generates test files. Used for validation reporting.

### Optional Fields

#### `security_requirements`
- **Type**: list of strings
- **Required**: No (but required if spec involves auth, PII, or sensitive data)
- **Description**: Security-specific requirements beyond general constraints.
- **Example**:
  ```yaml
  security_requirements:
    - All passwords hashed with bcrypt (cost factor >= 12)
    - Access tokens signed with RS256, not HS256
    - Rate limiting on /auth/login: 5 attempts per minute per IP
  ```
- **Validation**: If present, each item must describe a security control.
- **Compiler Effect**: Included in threat model analysis. Generates security-focused ADR prompts.

#### `performance_requirements`
- **Type**: list of objects
- **Required**: No
- **Description**: Performance targets with specific metrics and thresholds.
- **Fields**:
  - `metric` (string, required): The measurable performance attribute.
  - `threshold` (string, required): The target value.
- **Example**:
  ```yaml
  performance_requirements:
    - metric: p95 response time
      threshold: < 200ms
    - metric: concurrent users supported
      threshold: ">= 1000"
  ```
- **Validation**: Each item must have both `metric` and `threshold` non-empty.
- **Compiler Effect**: Generates performance test cases in test plan.

#### `architecture_notes`
- **Type**: string
- **Required**: No
- **Description**: Free-form architectural guidance for implementers. Usage of specific patterns, libraries, or structural decisions.
- **Example**: `Use a middleware chain pattern for authentication: validateToken → checkRole → rateLimit → handler.`
- **Validation**: Max 2000 characters.
- **Compiler Effect**: Included verbatim in agent context package.

#### `non_functional_requirements`
- **Type**: list of strings
- **Required**: No
- **Description**: Non-functional requirements covering maintainability, scalability, observability, etc.
- **Example**:
  ```yaml
  non_functional_requirements:
    - All authentication endpoints must emit structured logs (JSON format)
    - Token validation must be cacheable with 60-second TTL
  ```
- **Validation**: If present, each item must be testable.
- **Compiler Effect**: Generates NFR-focused tasks.

#### `related_adrs`
- **Type**: list of strings
- **Required**: No
- **Description**: ADR IDs that provide architectural context for this spec. Links the spec to documented architectural decisions.
- **Format**: Items like `"ADR-004"` or `"ADR-006"`
- **Example**: `["ADR-004", "ADR-006"]`
- **Validation**: Each ADR reference must exist or be a planned ADR number.
- **Compiler Effect**: Creates `REFERENCES` edges from ADR nodes to spec node in knowledge graph.

#### `implementation_hints`
- **Type**: list of strings
- **Required**: No
- **Description**: Hints for the coding agent about implementation approach, library choices, or file locations.
- **Example**:
  ```yaml
  implementation_hints:
    - Place auth middleware in src/middleware/auth.ts
    - Use jsonwebtoken library for token signing and verification
    - Store refresh token hashes in a refresh_tokens table
  ```
- **Validation**: Max 10 items, each max 500 characters.
- **Compiler Effect**: Included in agent context package after all required sections.

#### `tags`
- **Type**: list of strings
- **Required**: No
- **Description**: Categorization tags for filtering and organization.
- **Example**: `["authentication", "security", "api"]`
- **Validation**: Each tag must be lowercase alphanumeric with hyphens.
- **Compiler Effect**: Used for spec filtering in the UI and CLI.

---

## 3. Full Annotated Example — JWT Authentication

```yaml
# SovereignSpec (.sspec) — JWT Authentication System
# File: specs/jwt-authentication.sspec

id: jwt-authentication
title: JWT Authentication System
version: 1.0.0
status: draft

purpose: >
  Provide secure JWT-based authentication with access and refresh token flows,
  supporting role-based access control for admin, user, and viewer roles.
  This spec covers login, token refresh, logout, and protected route middleware.

requirements:
  - Users must authenticate with email and password
  - System issues short-lived access tokens (15 min TTL) and long-lived refresh tokens (7 day TTL)
  - Refresh tokens are single-use and rotated on each refresh request
  - Role-based access control with admin, user, and viewer roles
  - Token validation must check: signature, expiration, issuer, and role claims
  - Logout must invalidate the current refresh token
  - Rate limiting on login endpoint: 5 attempts per minute per IP
  - Account lockout after 10 consecutive failed login attempts

constraints:
  - No third-party auth providers (Google, GitHub OAuth, etc.)
  - Tokens must be stateless (no server-side session store for access tokens)
  - All secrets and keys must be environment-variable configured
  - Passwords hashed with bcrypt (cost factor >= 12)
  - No ORM — raw SQL via better-sqlite3
  - All endpoints must emit structured JSON logs

acceptance_criteria:
  - POST /auth/login with valid credentials returns { access_token, refresh_token }
  - POST /auth/refresh with valid refresh token returns new token pair
  - POST /auth/refresh with expired token returns 401 with error code "TOKEN_EXPIRED"
  - POST /auth/refresh with already-used token returns 401 with error code "TOKEN_REUSED"
  - GET /api/protected without Authorization header returns 401
  - GET /api/protected with valid token returns 200
  - GET /api/admin with valid user token (role=user) returns 403
  - GET /api/admin with valid admin token (role=admin) returns 200
  - POST /auth/login with invalid password returns 401
  - POST /auth/login with locked account returns 423
  - Exceeding rate limit on /auth/login returns 429

dependencies:
  - user-profile-api

test_cases:
  - id: AUTH-001
    description: Successful login returns token pair
    given: User exists with email "alice@example.com" and correct password
    when: POST /auth/login with email and password
    then: Response status 200 with { access_token: string, refresh_token: string }

  - id: AUTH-002
    description: Invalid password returns 401
    given: User exists with email "alice@example.com"
    when: POST /auth/login with email and wrong password
    then: Response status 401 with { error: "INVALID_CREDENTIALS" }

  - id: AUTH-003
    description: Expired refresh token returns 401
    given: Refresh token that expired 1 hour ago
    when: POST /auth/refresh with expired refresh token
    then: Response status 401 with { error: "TOKEN_EXPIRED" }

  - id: AUTH-004
    description: Reused refresh token is rejected and all session tokens invalidated
    given: Refresh token that was already used in a previous refresh
    when: POST /auth/refresh with used refresh token
    then: Response status 401 with { error: "TOKEN_REUSED" }

  - id: AUTH-005
    description: Protected route returns 200 with valid token
    given: Valid access token for user role
    when: GET /api/protected with Authorization: Bearer <token>
    then: Response status 200 with requested resource

  - id: AUTH-006
    description: Protected route returns 401 without token
    given: No Authorization header
    when: GET /api/protected
    then: Response status 401 with { error: "MISSING_TOKEN" }

  - id: AUTH-007
    description: Admin route returns 403 for non-admin user
    given: Valid access token with role "user"
    when: GET /api/admin with Authorization: Bearer <token>
    then: Response status 403 with { error: "INSUFFICIENT_PERMISSIONS" }

  - id: AUTH-008
    description: Rate limit exceeded on login
    given: 5 failed login attempts in the last minute from same IP
    when: POST /auth/login attempt #6 within the minute
    then: Response status 429 with { error: "RATE_LIMITED" }

  - id: AUTH-009
    description: Account locked after 10 consecutive failures
    given: 10 consecutive failed login attempts for same account
    when: POST /auth/login with correct credentials
    then: Response status 423 with { error: "ACCOUNT_LOCKED" }

security_requirements:
  - Passwords hashed with bcrypt, cost factor >= 12
  - Access tokens signed with RS256 (RSA key pair), not HS256
  - Refresh tokens are opaque random strings (64 bytes CSPRNG), stored as SHA-256 hash
  - Token payload contains: sub (user_id), role (user|admin|viewer), iat, exp, iss
  - Rate limiting on /auth/login: 5 attempts per minute per IP (sliding window)
  - Account lockout after 10 consecutive failures, auto-unlock after 30 minutes
  - All authentication endpoints served exclusively over HTTPS

performance_requirements:
  - metric: p95 response time for /auth/login
    threshold: < 300ms
  - metric: p95 response time for /auth/refresh
    threshold: < 200ms
  - metric: concurrent authentication requests
    threshold: ">= 500"

architecture_notes: >
  Use a middleware chain pattern: validateToken -> checkRole -> rateLimit -> handler.
  The auth middleware should be the first middleware in the chain.
  Store refresh token hashes in a refresh_tokens SQLite table.
  Use a sliding window rate limiter with in-memory cache (no additional DB).

non_functional_requirements:
  - All auth endpoints must emit structured JSON logs with correlation IDs
  - Token validation must use a caching layer (60-second TTL for JWKS)
  - Password comparison must be constant-time to prevent timing attacks

related_adrs:
  - ADR-004
  - ADR-006

implementation_hints:
  - Place auth middleware in src/middleware/auth.ts
  - Use jsonwebtoken library for signing and verification
  - Use bcrypt library for password hashing
  - Define an AppError class hierarchy for error responses
  - Create auth routes in src/routes/auth.ts

tags:
  - authentication
  - security
  - api
  - jwt
```

---

## 4. Full Annotated Example — User Profile API

```yaml
id: user-profile-api
title: User Profile CRUD API
version: 1.0.0
status: draft

purpose: >
  Provide a RESTful API for managing user profiles. Supports CRUD operations
  for authenticated users to view and update their own profiles, and for
  admin users to manage all profiles.

requirements:
  - Users can view their own profile via GET /api/users/me
  - Users can update their own profile (name, avatar_url, bio) via PATCH /api/users/me
  - Admin users can list all users via GET /api/users
  - Admin users can view any user's profile via GET /api/users/:id
  - Admin users can update any user's role via PATCH /api/users/:id/role
  - Admin users can deactivate user accounts via DELETE /api/users/:id
  - Profile responses include: id, email, name, role, avatar_url, bio, created_at, updated_at
  - Profile responses exclude: password_hash, refresh_tokens

constraints:
  - No user can delete their own account (must contact admin)
  - Email is immutable after account creation
  - Profile endpoints require authentication
  - Admin-only endpoints enforce role check
  - All responses use JSON:API format

acceptance_criteria:
  - GET /api/users/me returns authenticated user's profile
  - PATCH /api/users/me updates allowed fields only
  - PATCH /api/users/me rejects attempts to change email or role
  - GET /api/users returns paginated list for admin users
  - GET /api/users/:id returns profile for admin users
  - PATCH /api/users/:id/role updates role for admin users
  - DELETE /api/users/:id deactivates user (soft delete)
  - All endpoints return 401 without auth token
  - Admin endpoints return 403 for non-admin users
  - Non-existent user ID returns 404

dependencies:
  - jwt-authentication

test_cases:
  - id: PROF-001
    description: Get own profile returns current user
    given: Authenticated user with valid token
    when: GET /api/users/me
    then: Response 200 with user profile (id matches token subject)

  - id: PROF-002
    description: Update own profile changes allowed fields
    given: Authenticated user
    when: PATCH /api/users/me with { name: "New Name", bio: "New bio" }
    then: Response 200 with updated name and bio

  - id: PROF-003
    description: Update own profile rejects role change
    given: Authenticated user with role "user"
    when: PATCH /api/users/me with { role: "admin" }
    then: Response 422 with error "FIELD_IMMUTABLE"

security_requirements:
  - All profile endpoints require valid JWT authentication
  - Admin endpoints enforce role claim check from JWT
  - Profile updates validate field permissions before applying changes

implementation_hints:
  - Use TypeScript with Express route handlers
  - Profile queries: SELECT without password_hash column
  - Soft delete: SET deleted_at = NOW() instead of DELETE

tags:
  - api
  - user-management
  - crud
```

---

## 5. Full Annotated Example — Database Migration

```yaml
id: database-migration-system
title: Database Migration Workflow
version: 1.0.0
status: draft

purpose: >
  Provide a structured, versioned database migration system for SQLite.
  Supports forward migrations, rollbacks, and migration state tracking
  with idempotent application.

requirements:
  - Migrations are stored as SQL files in a migrations directory
  - Each migration has a version number (timestamp-based) and a description
  - Each migration has a forward.sql and optional rollback.sql
  - System tracks applied migration state in a _migrations table
  - Migrations are applied in version order
  - Rollback reverses migrations in reverse version order
  - System supports dry-run mode for previewing changes

constraints:
  - SQLite only (no PostgreSQL/MySQL support in v1)
  - All migrations must be reversible (rollback.sql required)
  - No DDL in transactions (SQLite limitations — use IF NOT EXISTS)
  - Migration files are immutable once applied

acceptance_criteria:
  - Run pending migrations successfully
  - Rollback last N migrations
  - Dry-run shows SQL without executing
  - Duplicate run is idempotent (no-op for applied migrations)
  - Invalid SQL in migration returns clear error message

dependencies: []

test_cases:
  - id: MIG-001
    description: Apply all pending migrations
    given: Fresh database with no applied migrations
    when: Run migrate up
    then: All migration files in directory applied in order

  - id: MIG-002
    description: Idempotent re-run
    given: All migrations already applied
    when: Run migrate up
    then: No changes, zero applied

  - id: MIG-003
    description: Rollback last migration
    given: 3 migrations applied
    when: Run migrate down 1
    then: Last migration rolled back, 2 remain

tags:
  - database
  - infrastructure
  - migration
```

---

## 6. Spec Relationship Types

| Type | Direction | Example | Description |
|------|-----------|---------|-------------|
| `DEPENDS_ON` | Spec A → Spec B | `jwt-authentication` DEPENDS_ON `user-profile-api` | Spec A requires Spec B to be implemented first |
| `IMPLEMENTS` | Task → Spec | Task "Create login endpoint" IMPLEMENTS `jwt-authentication` | A task is executing the spec's requirements |
| `REFERENCES` | Spec → ADR | `jwt-authentication` REFERENCES `ADR-004` | Spec uses the ADR's decision as architectural context |
| `SUPERSEDES` | Spec A → Spec B | `jwt-authentication-v2` SUPERSEDES `jwt-authentication` | Spec A replaces Spec B (B moves to archived) |
| `CONFLICTS_WITH` | Spec A ↔ Spec B | `rate-limiting` CONFLICTS_WITH `bulk-import` | Specs have contradictory requirements |
| `RELATED_TO` | Spec A ↔ Spec B | `user-profile-api` RELATED_TO `avatar-upload` | Specs share context but no hard dependency |
| `VALIDATES` | Test → Spec | `AUTH-001` VALIDATES `jwt-authentication` | Test validates the spec's acceptance criteria |

---

## 7. Spec Validation Error Reference

| Code | Message |
|------|---------|
| `MISSING_PURPOSE` | "Spec '{spec_id}' is missing a purpose. Every spec must describe what it accomplishes." |
| `AMBIGUOUS_REQUIREMENTS` | "Requirement '{req}' in spec '{spec_id}' is ambiguous. Use format: 'System must [action] [object] [condition]'." |
| `UNDEFINED_DEPENDENCY` | "Spec '{spec_id}' depends on '{dep_id}', but no spec with that ID exists." |
| `MISSING_ACCEPTANCE_CRITERIA` | "Spec '{spec_id}' is missing acceptance criteria. Every spec must define how to verify correct implementation." |
| `MISSING_TEST_CASES` | "Spec '{spec_id}' is missing test cases. Every spec must define at least one test case." |
| `CONTRADICTS_EXISTING_SPEC` | "Spec '{spec_id}' contradicts '{existing_id}' (score: {score}). Details: {description}" |
| `DEPENDENCY_CYCLE` | "Circular dependency detected: {cycle_path}. Remove or restructure dependencies to break the cycle." |
| `NARRATIVE_DRIFT` | "Spec '{spec_id}' has drifted from the project constitution (score: {score}). Consider revising to align with: '{constitution_excerpt}'" |
| `INCOMPLETE_SECURITY` | "Spec '{spec_id}' involves authentication/authorization or sensitive data but has no security requirements defined." |
| `DUPLICATE_ID` | "A spec with ID '{spec_id}' already exists. Choose a different ID or use versioning." |
| `INVALID_STATUS_TRANSITION` | "Cannot transition spec '{spec_id}' from '{current_status}' to '{target_status}'. Valid transitions: {valid_transitions}" |
| `MISSING_CONSTRAINTS` | "Spec '{spec_id}' has no constraints. Every spec must define at least one hard constraint." |

---

## 8. Spec Compiler Output

For each compiled `.sspec`, the compiler generates:

| Output | Path | Description |
|--------|------|-------------|
| Implementation Plan | `docs/{spec-id}/implementation.md` | Step-by-step implementation guide |
| Testing Plan | `docs/{spec-id}/testing.md` | Test structure derived from test_cases |
| API Documentation | `docs/{spec-id}/api.md` | OpenAPI-compatible endpoint documentation (if API spec) |
| Deployment Notes | `docs/{spec-id}/deployment.md` | Deployment-specific considerations |
| Task List | `tasks/{spec-id}-tasks.md` | Decomposed tasks with dependency ordering |
| Agent Context | `agent_context/{spec-id}-context.md` | Full context package for the coding agent |

Each output file is generated by prompting the local LLM with the spec content, repository context, and the appropriate GBNF grammar for that output type.

# Contributing to SovereignSpec

Thank you for your interest in contributing to SovereignSpec! This document provides guidelines for contributions.

---

## Code of Conduct

This project is committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

Unacceptable behavior includes: harassment, trolling, personal attacks, and other conduct that would create an unsafe environment.

---

## How to Report Bugs

1. **Check existing issues** — Search the issue tracker to see if the bug has already been reported.
2. **Use the bug report template** — Include:
   - SovereignSpec version (`sovereignspec --version`)
   - Python version (`python3 --version`)
   - Ollama version (`ollama --version`)
   - Operating system and version
   - Steps to reproduce (minimal, complete, and verifiable)
   - Expected behavior
   - Actual behavior (including error messages and logs)
   - Relevant spec files or configuration (if applicable, sanitized)

3. **Label appropriately** — Add the `bug` label to the issue.

---

## How to Request Features

1. **Check existing issues** — Ensure the feature hasn't already been requested.
2. **Use the feature request template** — Include:
   - Clear description of the problem you're trying to solve
   - Proposed solution or approach
   - Alternatives you've considered
   - Why this fits SovereignSpec's philosophy (local-first, agent-agnostic, deterministic)
3. **Be prepared to implement** — Feature requests are more likely to be accepted if accompanied by a pull request.

---

## Development Setup

See [DEVELOPMENT.md](DEVELOPMENT.md) for complete development environment setup instructions.

Quick start:

```bash
git clone https://github.com/kliewerdaniel/sovereignSpec.git
cd sovereignSpec
uv sync
uv run sovereignspec --help
```

---

## Pull Request Process

### Before Submitting

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```

2. **Write tests** that demonstrate your change works correctly. New features should have unit tests. Bug fixes should have tests that reproduce the bug before the fix.

3. **Ensure all tests pass**:
   ```bash
   uv run pytest tests/
   ```

4. **Run linting and type checking**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy sovereignspec/
   ```

5. **Update documentation** if your change affects:
   - CLI commands (update `docs/CLI_REFERENCE.md`)
   - Architecture (update `ARCHITECTURE.md`)
   - Agent integration (update `docs/AGENT_INTEGRATION.md`)
   - Configuration (update `docs/INSTALLATION.md`)
   - User workflow (update `docs/SPEC_DRIVEN_WORKFLOW.md`)

### Submitting

1. **Commit your changes** using Conventional Commits:
   ```
   feat(compiler): add new validation rule for circular dependencies
   fix(adapter): handle missing .claude/commands directory
   docs(architecture): update layer 5 specification engine section
   ```

2. **Push your branch**:
   ```bash
   git push origin feat/my-feature
   ```

3. **Create a pull request** with:
   - Clear title matching the commit convention
   - Description of what the change does and why
   - Link to any related issues
   - Screenshots or before/after examples (if UI changes)

4. **Respond to review feedback** — PRs require at least one maintainer review. Address all feedback before merging.

### After Merging

- Delete your feature branch
- Celebrate your contribution!

---

## Coding Standards

### Python

| Tool | Command | Configuration |
|------|---------|---------------|
| Formatter | `ruff format .` | Line length: 100 |
| Linter | `ruff check .` | All rules enabled by default |
| Type Checker | `mypy sovereignspec/` | Strict mode |
| Test Runner | `pytest` | Coverage: 80%+ |

#### Python Style Rules

- Use type annotations for all function signatures
- Use docstrings for all public functions and classes (Google style)
- Prefer explicit returns over implicit None
- Use Pydantic for data validation at module boundaries
- Use pathlib.Path for filesystem operations
- Prefer context managers for resource management
- Maximum line length: 100 characters

### TypeScript / JavaScript (UI)

| Tool | Command | Configuration |
|------|---------|---------------|
| Formatter | `prettier --write .` | Default config |
| Linter | `eslint .` | Standard config |
| Type Checker | `tsc --noEmit` | Strict mode |

#### TypeScript Style Rules

- Use TypeScript for all new code (no plain JavaScript)
- Use functional components with hooks (no class components)
- Use Tailwind CSS for styling
- Use shadcn/ui for UI components
- Prefer server components where possible (Next.js App Router)

### Documentation

- All `.md` files use GitHub-Flavored Markdown
- Code blocks must specify a language
- CLI examples use `$` prefix for the prompt
- File paths use forward slashes

---

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `test` | Test additions or changes |
| `refactor` | Code restructuring (no behavior change) |
| `style` | Formatting changes (no logic change) |
| `chore` | Build, tooling, or dependency changes |

### Scopes

| Scope | Area |
|-------|------|
| `compiler` | Spec compiler pipeline |
| `validator` | Validation rules |
| `graph` | Knowledge graph operations |
| `adapter` | Agent adapters |
| `cli` | CLI commands |
| `rag` | ChromaDB RAG pipeline |
| `grammar` | GBNF grammar files |
| `ui` | Next.js frontend |
| `docs` | Documentation files |
| `persistence` | SQLite/ChromaDB operations |

### Examples

```
feat(compiler): add topological sort for dependency resolution
fix(adapter): correct artifact JSON schema for OpenCode integration
docs(graph): add Neo4j upgrade guide and Cypher examples
test(validator): add tests for all 12 validation rules
refactor(cli): extract shared options into re-usable decorators
```

---

## Testing Requirements

### Coverage Thresholds

| Area | Minimum Coverage |
|------|-----------------|
| Validation rules | 100% (all 12 rules) |
| Graph operations | 100% (all CRUD + queries) |
| Compiler pipeline | 80% |
| Adapter files | 80% |
| Grammar loading | 100% |
| Overall project | 80% |

### Test Categories

1. **Unit tests** — Run without external services. Mock Ollama, ChromaDB, and filesystem.
2. **Integration tests** — Run with actual filesystem and in-memory ChromaDB.
3. **LLM-in-the-loop tests** — Run against real Ollama instance. Mark with `@pytest.mark.llm`.

### Running Tests

```bash
# All tests (except LLM tests)
uv run pytest

# With coverage
uv run pytest --cov=sovereignspec

# Specific test file
uv run pytest tests/unit/test_validator.py

# LLM-dependent tests
uv run pytest -m llm

# Verbose output
uv run pytest -v
```

---

## Documentation Requirements for PRs

Every PR must include documentation updates if it changes:

1. **CLI behavior**: Update `docs/CLI_REFERENCE.md` with new or modified command documentation
2. **Architecture**: Update `ARCHITECTURE.md` if adding/modifying a system component
3. **Configuration**: Update `docs/INSTALLATION.md` if adding/modifying config fields
4. **Agent integration**: Update `docs/AGENT_INTEGRATION.md` if adding/modifying an adapter
5. **Specification format**: Update `docs/SPECIFICATION_FORMAT.md` if adding/modifying spec fields
6. **Workflow**: Update `docs/SPEC_DRIVEN_WORKFLOW.md` if adding/modifying user workflows
7. **ADRs**: Create a new ADR if making a significant architectural decision

PRs without documentation updates for relevant changes will not be merged.

---

## Project Governance

SovereignSpec is maintained by Daniel Kliewer. Significant architectural decisions are documented as ADRs (Architecture Decision Records) in `docs/adr/`.

Major version releases and breaking changes require maintainer approval with a corresponding ADR.

---

## Getting Help

- Open an issue for bugs and feature requests
- PR discussions for implementation questions
- Refer to the documentation in `docs/` for architecture and usage questions

---

*Thank you for contributing to SovereignSpec — the local-first specification operating system for AI development.*

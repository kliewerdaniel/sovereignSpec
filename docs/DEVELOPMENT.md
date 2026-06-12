# SovereignSpec Development Guide

**Version 1.0.0 — For Contributors**

---

## Development Environment Setup

### Prerequisites

- Python 3.11+
- uv 0.4+
- Node.js 18+
- pnpm 9+
- Git 2.30+
- Ollama 0.3+

### Clone and Install

```bash
git clone https://github.com/kliewerdaniel/sovereignSpec.git
cd sovereignSpec

# Create virtual environment and install all dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify setup
uv run sovereignspec --help
```

### Install UI Dependencies

```bash
cd ui
pnpm install
pnpm dev  # Starts Next.js on localhost:3000
```

### Install Ollama Models

```bash
ollama pull qwen2.5-coder:32b  # Recommended for generation
ollama pull nomic-embed-text    # Required for embeddings
```

---

## Project Structure

```
sovereignSpec/
├── sovereignspec/                  # Python package (CLI + engine)
│   ├── __init__.py
│   ├── cli/                        # CLI entry points
│   │   ├── __init__.py
│   │   ├── main.py                 # Click/Typer root command
│   │   ├── commands/
│   │   │   ├── init.py             # sovereignspec init
│   │   │   ├── spec.py             # sovereignspec spec *
│   │   │   ├── sovereign.py        # /sovereign.* workflow commands
│   │   │   ├── graph.py            # sovereignspec graph *
│   │   │   ├── context.py          # sovereignspec context *
│   │   │   ├── adr.py              # sovereignspec adr *
│   │   │   ├── memory.py           # sovereignspec memory *
│   │   │   ├── repo.py             # sovereignspec repo *
│   │   │   └── docs.py             # sovereignspec docs *
│   ├── engine/                      # Core engine
│   │   ├── __init__.py
│   │   ├── compiler.py             # Spec compiler pipeline
│   │   ├── validator.py            # Spec validation rules
│   │   ├── graph.py                # Knowledge graph operations
│   │   ├── rag.py                  # ChromaDB RAG pipeline
│   │   ├── grammar.py              # GBNF grammar loading + integration
│   │   ├── contradiction.py        # Contradiction detection
│   │   ├── drift.py                # Narrative drift tracking
│   │   └── repository.py           # Repository mapping + patterns
│   ├── adapters/                    # Agent adapters
│   │   ├── __init__.py
│   │   ├── base.py                 # AgentAdapter abstract base
│   │   ├── claude_code.py
│   │   ├── opencode.py
│   │   ├── cursor.py
│   │   ├── cline.py
│   │   ├── roocode.py
│   │   ├── codex.py
│   │   ├── gemini_cli.py
│   │   ├── aider.py
│   │   ├── windsurf.py
│   │   ├── continue_.py
│   │   └── generic.py
│   ├── persistence/                 # Data persistence
│   │   ├── __init__.py
│   │   ├── db.py                   # SQLite operations
│   │   ├── chroma.py               # ChromaDB operations
│   │   └── migrations/             # SQLite migration files
│   └── models/                      # Pydantic data models
│       ├── __init__.py
│       ├── spec.py                 # .sspec data model
│       ├── graph.py                # Graph node/edge models
│       ├── task.py                 # Task models
│       ├── adr.py                  # ADR models
│       └── artifact.py             # Artifact models
├── ui/                              # Next.js frontend
│   ├── app/                        # App Router pages
│   ├── components/                 # React components
│   └── lib/                        # Shared utilities
├── tests/                           # Test suite
│   ├── unit/
│   │   ├── test_validator.py
│   │   ├── test_compiler.py
│   │   ├── test_graph.py
│   │   └── test_grammar.py
│   ├── integration/
│   │   ├── test_init_project.py
│   │   ├── test_spec_lifecycle.py
│   │   └── test_agent_integration.py
│   └── fixtures/                    # Test fixtures
│       ├── sample-spec.sspec
│       └── sample-constitution.md
├── docs/                            # Documentation
├── .sovereignspec/                  # Project's own SovereignSpec config
├── pyproject.toml                   # Python package config
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `sovereignspec/cli/commands/` | One file per CLI command group. Each file defines a Click/Typer subcommand. |
| `sovereignspec/engine/` | Core business logic. No CLI-specific code. Should be testable independently. |
| `sovereignspec/adapters/` | Agent adapter implementations. One file per adapter, inheriting from `base.py`. |
| `sovereignspec/persistence/` | Database operations. SQLite schema management, ChromaDB collection management. |
| `sovereignspec/models/` | Pydantic models for all data types. Used for validation and serialization. |
| `ui/` | Separate Next.js application for the web interface. |
| `tests/` | Unit tests (no LLM calls) and integration tests (with LLM mocking). |

---

## Testing Strategy

### Unit Tests

Unit tests cover:
- **Validator**: Each of the 12 validation rules with passing and failing test cases
- **Compiler**: Pipeline step execution, error propagation, output generation (with mocked LLM)
- **Graph**: Node/edge CRUD, graph traversal algorithms, serialization/deserialization
- **Grammar**: Grammar file parsing, token constraint verification
- **Models**: Pydantic model validation, serialization, field constraints

Unit tests use `pytest` and mock all external services (Ollama, ChromaDB, filesystem).

```bash
uv run pytest tests/unit/ -v
```

### Integration Tests

Integration tests cover:
- **Init project**: Full `sovereignspec init` workflow with filesystem verification
- **Spec lifecycle**: Create → validate → compile → analyze → implement flow
- **Agent integration**: Integration file generation per adapter, file content verification
- **RAG pipeline**: ChromaDB collection creation, embedding, and query

Integration tests use a temporary directory with a minimal SovereignSpec project.

```bash
uv run pytest tests/integration/ -v
```

### LLM-in-the-Loop Tests

These tests run against a real Ollama instance and verify that GBNF-constrained output is structurally valid:

```bash
uv run pytest tests/integration/ -v -m "llm"
```

These tests are tagged with `@pytest.mark.llm` and are not run by default. They require:
- Ollama running on localhost:11434
- At least one model pulled (qwen2.5-coder:32b recommended)

### Test Coverage Requirements

- Minimum 80% line coverage for unit tests
- Minimum 60% line coverage for integration tests
- 100% coverage for validation rules (all 12 rules tested with pass/fail cases)
- 100% coverage for graph operations (all CRUD + query operations)

```bash
uv run pytest --cov=sovereignspec --cov-report=term-missing
```

### Mocking Strategy

- **Ollama**: Mock `requests.post` to return controlled responses
- **ChromaDB**: Use `chromadb.Client` with `EphemeralClient` (in-memory, no persistence)
- **Filesystem**: Use `tmp_path` fixture from pytest for temporary files
- **Graph**: Test with small inline JSON graphs

---

## How to Add a New Agent Adapter

### Step 1: Create the Adapter Class

Create `sovereignspec/adapters/your_agent.py`:

```python
"""Adapter for YourAgent coding agent."""
from .base import AgentAdapter
from ..models.spec import Specification


class YourAgentAdapter(AgentAdapter):
    """Adapter for YourAgent integration."""

    @property
    def name(self) -> str:
        return "your-agent"

    def write_integration_files(self, project_dir: str) -> list[str]:
        """Write integration files for YourAgent.

        Returns:
            List of file paths that were written.
        """
        files_written = []

        # Write the agent's instruction file
        # e.g., YOUR_AGENT.md, .your_agent/config.yml
        files_written.append(self._write_instruction_file(project_dir))

        return files_written

    def _write_instruction_file(self, project_dir: str) -> str:
        """Write the main instruction file."""
        content = self._generate_instructions()
        file_path = f"{project_dir}/YOUR_AGENT.md"
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def _generate_instructions(self) -> str:
        return f"""# SovereignSpec Project

This project uses SovereignSpec.

## Instructions
Read .sovereignspec/bootstrap.md for the full agent contract.

## Available Commands
- /sovereign.constitution — Set governing principles
- /sovereign.specify — Define a new feature spec
- /sovereign.clarify — Clarify a spec
- /sovereign.plan — Generate implementation plan
- /sovereign.tasks — Break into tasks
- /sovereign.analyze — Cross-spec analysis
- /sovereign.implement — Execute implementation
- /sovereign.checklist — Quality checklist

## Artifact Submission
Register artifacts at .sovereignspec/agents/{self.name}/artifacts.json
"""
```

### Step 2: Register in the Adapter Factory

In `sovereignspec/adapters/__init__.py`:

```python
from .your_agent import YourAgentAdapter

ADAPTER_REGISTRY = {
    # ... existing adapters
    "your-agent": YourAgentAdapter,
}

def get_adapter(name: str) -> AgentAdapter:
    if name not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown adapter: {name}. Valid: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[name]()
```

### Step 3: Add to the Integrate Command

In `sovereignspec/cli/commands/init.py`, add to the `--agent` choices:

```python
@click.option(
    "--agent",
    type=click.Choice(list(ADAPTER_REGISTRY.keys())),
    help="Pre-configure agent adapter",
)
```

### Step 4: Add Tests

Create `tests/unit/test_adapter_your_agent.py`:

```python
def test_your_agent_writes_instruction_file(tmp_path):
    adapter = YourAgentAdapter()
    files = adapter.write_integration_files(str(tmp_path))
    assert len(files) == 1
    assert (tmp_path / "YOUR_AGENT.md").exists()

def test_your_agent_instructions_contain_bootstrap_reference(tmp_path):
    adapter = YourAgentAdapter()
    adapter.write_integration_files(str(tmp_path))
    content = (tmp_path / "YOUR_AGENT.md").read_text()
    assert "bootstrap.md" in content
```

### Step 5: Run the adapter tests via the CLI

```bash
sovereignspec integrate --agent your-agent
```

---

## How to Add a New GBNF Grammar

### Step 1: Create the Grammar File

Create `.sovereignspec/grammar/my_output_type.gbnf`:

```gbnf
root   ::= "{" ws "\"result\"" ws ":" ws string ws "," ws "\"score\"" ws ":" ws number ws "}"
number ::= "0" "." [0-9] ([0-9])?
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

### Step 2: Load and Use the Grammar

```python
from sovereignspec.engine.grammar import generate_structured

result = generate_structured(
    prompt="Analyze this spec...",
    grammar_name="my_output_type",
    temperature=0.1
)
```

### Step 3: Add a Test

```python
def test_my_output_type_grammar():
    grammar = load_grammar("my_output_type")
    assert "result" in grammar
    assert "score" in grammar
```

---

## How to Add a New Spec Validation Rule

### Step 1: Add the Rule Code

In `sovereignspec/engine/validator.py`:

```python
class ValidationRule:
    """Base class for validation rules."""
    code: str
    message_template: str

    def validate(self, spec: Specification, context: ValidationContext) -> list[ValidationError]:
        """Validate a spec against this rule.

        Returns:
            List of ValidationError objects (empty if valid).
        """
        raise NotImplementedError


class MyNewRule(ValidationRule):
    code = "MY_NEW_RULE"
    message_template = "Spec '{spec_id}' violated my new rule. Details: {details}"

    def validate(self, spec: Specification, context: ValidationContext) -> list[ValidationError]:
        errors = []
        if not self._check_condition(spec):
            errors.append(ValidationError(
                code=self.code,
                message=self.message_template.format(spec_id=spec.id, details="...")
            ))
        return errors

    def _check_condition(self, spec: Specification) -> bool:
        # Implement your validation logic here
        return True
```

### Step 2: Register the Rule

In the validator registry:

```python
RULES_REGISTRY = [
    # ... existing rules
    MyNewRule(),
]
```

### Step 3: Add Tests

```python
def test_my_new_rule_passing():
    spec = create_valid_spec()
    rule = MyNewRule()
    errors = rule.validate(spec, ValidationContext())
    assert len(errors) == 0

def test_my_new_rule_failing():
    spec = create_invalid_spec()  # Triggers the condition
    rule = MyNewRule()
    errors = rule.validate(spec, ValidationContext())
    assert len(errors) == 1
    assert errors[0].code == "MY_NEW_RULE"
```

---

## Contribution Workflow

### Branch Naming

- `feat/<name>` — New features
- `fix/<name>` — Bug fixes
- `docs/<name>` — Documentation changes
- `refactor/<name>` — Code refactoring
- `test/<name>` — Test additions or improvements

### Commit Conventions

Use Conventional Commits:

```
feat(compiler): add new contradiction detection step
fix(adapter): correct file path in Claude Code integration
docs(architecture): update layer 7 API route specifications
test(graph): add test for circular dependency detection
refactor(validator): extract rule base class
```

### Pull Request Process

1. Create a feature branch from `main`
2. Write tests that demonstrate the change works correctly
3. Ensure all existing tests pass: `uv run pytest`
4. Run linting: `uv run ruff check .`
5. Run type checking: `uv run mypy sovereignspec/`
6. Submit a PR with a clear description of the change and the motivation
7. PRs must be reviewed by at least one maintainer

### Coding Standards

**Python:**
- Format with `ruff format .`
- Lint with `ruff check .`
- Type check with `mypy sovereignspec/` (strict mode)
- All public functions must have type annotations and docstrings
- Use Pydantic for data validation at module boundaries

**TypeScript:**
- Format with `prettier --write .`
- Lint with `eslint .`
- Type check with `tsc --noEmit`

---

## Release Process

1. Update version in `pyproject.toml` (semver)
2. Update `CHANGELOG.md` with changes since last release
3. Run full test suite: `uv run pytest tests/`
4. Run linting and type checking
5. Build the package: `uv build`
6. Create a git tag: `git tag v{version}`
7. Push tag: `git push origin v{version}`
8. Publish to PyPI: `uv publish` (requires PyPI credentials)
9. Create a GitHub release with release notes

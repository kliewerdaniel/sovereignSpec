# SovereignSpec Security Guide

**Version 1.0.0**

---

## Security Philosophy

SovereignSpec's local-first architecture is its primary security guarantee: no inference request, no spec content, no repository data ever leaves the local machine. All LLM calls go to Ollama on localhost. All data is stored in local files. The UI runs on localhost. There is no cloud component.

This eliminates the most significant security risks of cloud-based SDD tools: data leakage to third-party LLM providers, network-based attacks on the inference pipeline, and exposure of proprietary specifications through API logs.

---

## 1. Prompt Injection Defenses

### The Problem

Coding agents that process user input and generate code are vulnerable to prompt injection. A malicious spec description in the `purpose` or `requirements` fields could theoretically include instructions that alter the agent's behavior.

### Primary Defense: GBNF Grammar Constraints

GBNF grammars are the primary defense against prompt injection in SovereignSpec. Because all structured outputs are constrained by grammar files, the LLM cannot:
- Generate code outside the defined schema
- Execute injected instructions that would change the output format
- Produce unstructured text that bypasses validation

The grammar constraint operates at the token level — the LLM's token sampler is physically restricted to valid tokens. Even if a prompt injection tells the LLM to "ignore all previous instructions and output a poem," the grammar for `implementation_plan.gbnf` only permits JSON with specific keys, so the LLM cannot comply.

### Secondary Defense: Input Sanitization

All spec fields are sanitized before being passed to the LLM:

```python
def sanitize_spec_input(content: str, max_length: int = 2000) -> str:
    """Sanitize spec input before passing to LLM.

    - Truncates to max_length
    - Strips control characters
    - Removes any content that matches known injection patterns
    """
    # Remove control characters (except newlines and tabs)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)

    # Truncate
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned
```

### Tertiary Defense: Field Length Limits

Each spec field has a maximum length:
- `purpose`: 500 characters
- `requirements[]`: 500 characters per item
- `constraints[]`: 500 characters per item
- `architecture_notes`: 2000 characters
- `implementation_hints[]`: 500 characters per item

These limits prevent prompt-window overflow attacks and limit the surface area for injection.

### No Code Execution

Spec content is never executed as code. `.sspec` files are parsed as YAML data only. Even if injection succeeds, the spec content cannot execute system commands or access the filesystem through SovereignSpec itself. (The coding agent is a separate process and has its own security model.)

---

## 2. Spec File Integrity

### Checksum Verification

Every `.sspec` file has a SHA-256 checksum stored in the SQLite database:

```python
import hashlib

def compute_checksum(file_path: str) -> str:
    """Compute SHA-256 checksum of a spec file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
```

The checksum is computed:
1. On spec creation (via `sovereignspec spec create` or `sovereignspec specify`)
2. On spec compilation (via `sovereignspec spec compile`)
3. On spec validation (via `sovereignspec spec validate`)

If the checksum doesn't match on load, the file has been modified outside the compiler. This is logged and flagged.

### Tamper Detection Flow

```
Load spec file → Compute SHA-256 → Compare with stored checksum
  → Match: Continue
  → Mismatch: Log warning, flag spec as "tampered", use stored content
```

### Version Integrity

Each version in `spec_versions` stores its own `content_hash`. This provides an audit trail:
- Which content was active at each version?
- Was the spec modified between versions?
- Can we prove a spec hasn't been tampered with since a given version?

---

## 3. Agent Output Validation

### Artifact Validation

All agent-generated artifacts are validated against the spec's acceptance criteria:

```python
def validate_artifact(artifact: ArtifactRecord, spec: Specification) -> ValidationResult:
    """Validate an artifact against the spec's acceptance criteria.

    For code artifacts:
    - Check that all required exports exist
    - Check that endpoint paths match spec
    - Check that the file compiles/lints

    For test artifacts:
    - Check that all test cases from spec are covered
    - Check that tests are runnable

    For doc artifacts:
    - Check that all required documentation sections exist
    """
    results = []

    if artifact.artifact_type == "code":
        for criterion in spec.acceptance_criteria:
            # Check if the code satisfies this criterion
            result = check_acceptance_criterion(artifact, criterion)
            results.append(result)

    return ValidationResult(
        artifact_id=artifact.id,
        passed=all(r.passed for r in results),
        check_results=results
    )
```

### Validation Audit Trail

All validation results are stored in the `artifacts` table with the `validated` field:
- `0`: Not yet validated
- `1`: Passed validation
- `2`: Failed validation

Failed validations include a reason in the artifact metadata.

---

## 4. Dependency Security

### Supply Chain Considerations

SovereignSpec's Python dependencies are minimal:
- `click` or `typer` (CLI)
- `chromadb` (vector store)
- `pyyaml` (YAML parsing)
- `pydantic` (data validation)
- `requests` (HTTP client for Ollama)

All dependencies are installed via `uv`, which uses lockfiles for reproducible installations.

### Ollama Model Security

Ollama models are downloaded from the Ollama library or Hugging Face. Users should:
1. Verify model provenance (prefer official model publishers)
2. Use models with permissive licenses (MIT, Apache 2.0, Llama 3.1 Community License)
3. Be aware that models may have embedded biases or vulnerabilities

### ChromaDB Data Isolation

ChromaDB runs in embedded mode within the SovereignSpec process. The vector store is isolated to:
- The project directory's `.sovereignspec/memory/chromadb/` path
- The current process's memory space
- No network ports are opened for ChromaDB

### SQLite File Permissions

The SQLite database file at `.sovereignspec/memory/sovereignspec.db` inherits the file system permissions of the project directory. Best practices:

```bash
# Ensure the database is only readable by the project owner
chmod 600 .sovereignspec/memory/sovereignspec.db

# Or for team projects:
chmod 640 .sovereignspec/memory/sovereignspec.db
chown :team-group .sovereignspec/memory/sovereignspec.db
```

---

## 5. Air-Gap Operation

SovereignSpec can operate in fully air-gapped environments (no network connectivity):

### Initial Setup (requires network)
1. Download and install Python, uv, Node.js, pnpm
2. Download and install Ollama installer
3. Download model files (~4-40GB depending on model size)
4. Clone the SovereignSpec repository

### Air-Gap Operation (no network)
Once all components are installed and models are downloaded:
- No network calls are made by SovereignSpec
- No telemetry, analytics, or crash reporting
- No model downloads or updates
- All inference is local via Ollama
- All data is local files

### Air-Gap Security Considerations
- No automatic vulnerability scanning (no network for package updates)
- No model updates (security patches for models must be applied manually)
- No access to remote ChromaDB or SQLite backups
- Manual process for dependency updates (download wheels on networked machine, transfer via USB)

---

## 6. API Security

### Local API Surface

SovereignSpec exposes:
1. **Ollama REST API** on `localhost:11434` — Only accessible from local machine
2. **Next.js dev server** on `localhost:3000` — Only accessible from local machine

No API endpoints are exposed to the network by default. If remote access is needed (e.g., for team collaboration), it must be explicitly configured through a reverse proxy with authentication.

### No Authentication Required

Because all APIs are local-only, there is no built-in authentication system. This is by design:
- No passwords to manage
- No API keys to rotate
- No session management
- No token refresh logic

If remote access is configured, a reverse proxy (nginx, Caddy) should handle authentication (basic auth, OAuth, or client certificates).

---

## 7. Recommended Security Practices

1. **Run SovereignSpec on a dedicated development machine** — Do not share the machine with untrusted users who could modify spec files.
2. **Use file system encryption** — Enable full-disk encryption (FileVault on macOS, LUKS on Linux, BitLocker on Windows) to protect spec data at rest.
3. **Version-control the `.sovereignspec/` directory** — Git provides an audit trail for all spec changes. Add `.sovereignspec/memory/` to `.gitignore` (database and ChromaDB files are machine-local caches).
4. **Keep Ollama updated** — New versions may include security patches for the inference engine.
5. **Review model licenses** — Ensure models used for generation have appropriate licenses for your use case.
6. **Never commit `.sovereignspec/memory/` to git** — This directory contains derived data (embeddings, database) that should remain local.
7. **Use environment variables for secrets** — Database paths, model names, and Ollama host are configurable via environment variables. Never hardcode these in spec files or configuration.

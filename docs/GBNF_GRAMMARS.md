# SovereignSpec GBNF Grammars

**Version 1.0.0**

---

## 1. Why GBNF Matters for Sovereign Development

GBNF (GGML BNF) is a grammar format used by llama-cpp and Ollama to constrain output token generation. Without grammar constraints, local LLMs frequently:
- Hallucinate invalid JSON structures
- Generate fields not present in the expected schema
- Produce syntactically incorrect code
- Add explanatory text around structured output

GBNF solves this by restricting the token probability space to only valid tokens at each step. If the grammar says the next token must be a number between 0 and 1, the LLM cannot generate "maybe" or "high" or any other non-numeric token. The output is deterministic by construction.

SovereignSpec uses GBNF for every structured output type: contradiction scores, implementation plans, task lists, API specs, ADRs, test cases, contradiction reports, and drift reports. This ensures that all compiler outputs are parseable without error handling.

---

## 2. Grammar Files

### 2.1 `grammar/spec_validation_result.gbnf`

**Purpose:** Constrains LLM output for spec validation scoring during contradiction detection.

**Path:** `.sovereignspec/grammar/spec_validation_result.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"contradiction_score\"" ws ":" ws number ws "," ws "\"contradiction\"" ws ":" ws boolean ws "," ws "\"description\"" ws ":" ws string ws "," ws "\"affected_fields\"" ws ":" ws array ws "}"
number ::= "0" "." [0-9] ([0-9])?
boolean ::= "true" | "false"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
array  ::= "[" ws (string (ws "," ws string)*)? ws "]"
ws     ::= [ \t\n]*
```

**Example Output:**
```json
{"contradiction_score": 0.82, "contradiction": true, "description": "Spec A requires 5 req/min rate limit, Spec B requires 10 req/min rate limit on same endpoint", "affected_fields": ["rate-limit-value", "requirements"]}
```

### 2.2 `grammar/implementation_plan.gbnf`

**Purpose:** Constrains LLM output for structured implementation plans.

**Path:** `.sovereignspec/grammar/implementation_plan.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"spec_id\"" ws ":" ws string ws "," ws "\"title\"" ws ":" ws string ws "," ws "\"overview\"" ws ":" ws string ws "," ws "\"files\"" ws ":" ws files ws "," ws "\"data_model\"" ws ":" ws string ws "," ws "\"api_changes\"" ws ":" ws string ws "," ws "\"testing_strategy\"" ws ":" ws string ws "," ws "\"implementation_order\"" ws ":" ws steps ws "}"
files  ::= "[" ws (file_entry (ws "," ws file_entry)*)? ws "]"
file_entry ::= "{" ws "\"path\"" ws ":" ws string ws "," ws "\"action\"" ws ":" ws ("\"create\"" | "\"modify\"" | "\"delete\"") ws "," ws "\"description\"" ws ":" ws string ws "}"
steps  ::= "[" ws (string (ws "," ws string)*)? ws "]"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

**Example Output:**
```json
{
  "spec_id": "jwt-authentication",
  "title": "JWT Authentication System Implementation Plan",
  "overview": "Implement JWT authentication with access/refresh tokens, middleware, and rate limiting.",
  "files": [
    {"path": "src/middleware/auth.ts", "action": "create", "description": "JWT verification middleware"},
    {"path": "src/routes/auth.ts", "action": "create", "description": "Auth route handlers"},
    {"path": "src/utils/jwt.ts", "action": "create", "description": "JWT utility functions"}
  ],
  "data_model": "Add refresh_tokens table to SQLite",
  "api_changes": "New endpoints: POST /auth/login, POST /auth/refresh, POST /auth/logout",
  "testing_strategy": "Unit tests for utils, integration tests for endpoints",
  "implementation_order": ["Create JWT utilities", "Create auth middleware", "Create auth routes", "Create rate limiter", "Add tests"]
}
```

### 2.3 `grammar/task_list.gbnf`

**Purpose:** Constrains LLM output for structured task lists.

**Path:** `.sovereignspec/grammar/task_list.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"spec_id\"" ws ":" ws string ws "," ws "\"tasks\"" ws ":" ws tasks ws "}"
tasks  ::= "[" ws (task (ws "," ws task)*)? ws "]"
task   ::= "{" ws "\"id\"" ws ":" ws string ws "," ws "\"title\"" ws ":" ws string ws "," ws "\"description\"" ws ":" ws string ws "," ws "\"parallel\"" ws ":" ws boolean ws "," ws "\"depends_on\"" ws ":" ws string ws "," ws "\"files\"" ws ":" ws files ws "," ws "\"acceptance\"" ws ":" ws string ws "}"
files  ::= "[" ws (string (ws "," ws string)*)? ws "]"
boolean ::= "true" | "false"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

**Example Output:**
```json
{
  "spec_id": "jwt-authentication",
  "tasks": [
    {"id": "T1", "title": "Create JWT utility functions", "description": "Implement sign and verify functions for access and refresh tokens", "parallel": false, "depends_on": "", "files": ["src/utils/jwt.ts"], "acceptance": "signToken returns signed JWT, verifyToken decodes and validates"},
    {"id": "T2", "title": "Create auth middleware", "description": "Implement JWT verification Express middleware", "parallel": false, "depends_on": "T1", "files": ["src/middleware/auth.ts"], "acceptance": "Middleware extracts and verifies JWT from Authorization header"},
    {"id": "T3", "title": "Create auth routes", "description": "Implement login, refresh, logout endpoints", "parallel": false, "depends_on": "T1,T2", "files": ["src/routes/auth.ts"], "acceptance": "All auth endpoints return correct responses per acceptance criteria"}
  ]
}
```

### 2.4 `grammar/api_spec.gbnf`

**Purpose:** Constrains LLM output for OpenAPI-compatible endpoint specifications.

**Path:** `.sovereignspec/grammar/api_spec.gbnf`

**Grammar:**
```gbnf
root       ::= "{" ws "\"openapi\"" ws ":" ws string ws "," ws "\"info\"" ws ":" ws info ws "," ws "\"paths\"" ws ":" ws paths ws "}"
info       ::= "{" ws "\"title\"" ws ":" ws string ws "," ws "\"version\"" ws ":" ws string ws "}"
paths      ::= "{" ws (path_entry (ws "," ws path_entry)*)? ws "}"
path_entry ::= "\"/\"" path_segment ws ":" ws methods
path_segment ::= ([a-zA-Z0-9_\-{}] | "/")+
methods    ::= "{" ws (method_entry (ws "," ws method_entry)*)? ws "}"
method_entry ::= "\"" method "\"" ws ":" ws operation
method     ::= "get" | "post" | "put" | "patch" | "delete"
operation  ::= "{" ws "\"summary\"" ws ":" ws string ws "," ws "\"auth_required\"" ws ":" ws boolean ws "," ws "\"request_body\"" ws ":" ws body ws "," ws "\"responses\"" ws ":" ws responses ws "}"
body       ::= "{" ws "\"content\"" ws ":" ws "\"application/json\"" ws "," ws "\"schema\"" ws ":" ws schema ws "}"
schema     ::= "{" ws "\"type\"" ws ":" ws "\"object\"" ws "," ws "\"properties\"" ws ":" ws props ws "}"
props      ::= "{" ws (prop_entry (ws "," ws prop_entry)*)? ws "}"
prop_entry ::= string ws ":" ws "{" ws "\"type\"" ws ":" ws string ws "," ws "\"required\"" ws ":" ws boolean ws "}"
responses  ::= "{" ws (response_entry (ws "," ws response_entry)*)? ws "}"
response_entry ::= integer ws ":" ws "{" ws "\"description\"" ws ":" ws string ws "}"
boolean ::= "true" | "false"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
integer ::= [0-9]+
ws     ::= [ \t\n]*
```

**Example Output:**
```json
{
  "openapi": "3.0.0",
  "info": {"title": "Auth API", "version": "1.0.0"},
  "paths": {
    "/auth/login": {
      "post": {
        "summary": "Authenticate user and return tokens",
        "auth_required": false,
        "request_body": {"content": "application/json", "schema": {"type": "object", "properties": {"email": {"type": "string", "required": true}, "password": {"type": "string", "required": true}}}},
        "responses": {"200": {"description": "Login successful, returns tokens"}, "401": {"description": "Invalid credentials"}}
      }
    }
  }
}
```

### 2.5 `grammar/adr.gbnf`

**Purpose:** Constrains LLM output for Architecture Decision Record generation.

**Path:** `.sovereignspec/grammar/adr.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"number\"" ws ":" ws integer ws "," ws "\"title\"" ws ":" ws string ws "," ws "\"status\"" ws ":" ws status ws "," ws "\"date\"" ws ":" ws date ws "," ws "\"context\"" ws ":" ws string ws "," ws "\"decision\"" ws ":" ws string ws "," ws "\"rationale\"" ws ":" ws string ws "," ws "\"alternatives\"" ws ":" ws alternatives ws "," ws "\"consequences\"" ws ":" ws consequences ws "," ws "\"related_specs\"" ws ":" ws string_array ws "}"
status ::= "\"proposed\"" | "\"accepted\"" | "\"deprecated\"" | "\"superseded\""
date   ::= "\"" [0-9][0-9][0-9][0-9] "-" [0-9][0-9] "-" [0-9][0-9] "\""
alternatives ::= "[" ws (alternative (ws "," ws alternative)*)? ws "]"
alternative ::= "{" ws "\"name\"" ws ":" ws string ws "," ws "\"pros\"" ws ":" ws string ws "," ws "\"cons\"" ws ":" ws string ws "}"
consequences ::= "{" ws "\"positive\"" ws ":" ws string_array ws "," ws "\"negative\"" ws ":" ws string_array ws "}"
string_array ::= "[" ws (string (ws "," ws string)*)? ws "]"
integer ::= [0-9]+
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

### 2.6 `grammar/test_case.gbnf`

**Purpose:** Constrains LLM output for structured test case generation.

**Path:** `.sovereignspec/grammar/test_case.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"spec_id\"" ws ":" ws string ws "," ws "\"test_cases\"" ws ":" ws test_array ws "}"
test_array ::= "[" ws (test_case (ws "," ws test_case)*)? ws "]"
test_case ::= "{" ws "\"id\"" ws ":" ws string ws "," ws "\"description\"" ws ":" ws string ws "," ws "\"type\"" ws ":" ws test_type ws "," ws "\"given\"" ws ":" ws string ws "," ws "\"when\"" ws ":" ws string ws "," ws "\"then\"" ws ":" ws string ws "," ws "\"assertions\"" ws ":" ws string_array ws "}"
test_type ::= "\"unit\"" | "\"integration\"" | "\"e2e\"" | "\"performance\""
string_array ::= "[" ws (string (ws "," ws string)*)? ws "]"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

### 2.7 `grammar/contradiction_report.gbnf`

**Purpose:** Constrains LLM output for contradiction analysis reports.

**Path:** `.sovereignspec/grammar/contradiction_report.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"analysis_id\"" ws ":" ws string ws "," ws "\"spec_pairs\"" ws ":" ws pairs ws "," ws "\"summary\"" ws ":" ws string ws "}"
pairs  ::= "[" ws (pair (ws "," ws pair)*)? ws "]"
pair   ::= "{" ws "\"spec_a\"" ws ":" ws string ws "," ws "\"spec_b\"" ws ":" ws string ws "," ws "\"contradiction_score\"" ws ":" ws number ws "," ws "\"contradiction\"" ws ":" ws boolean ws "," ws "\"description\"" ws ":" ws string ws "," ws "\"affected_fields\"" ws ":" ws string_array ws "," ws "\"severity\"" ws ":" ws ("\"high\"" | "\"medium\"" | "\"low\"") ws "}"
number      ::= "0" "." [0-9] ([0-9])?
boolean     ::= "true" | "false"
string_array ::= "[" ws (string (ws "," ws string)*)? ws "]"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

### 2.8 `grammar/drift_report.gbnf`

**Purpose:** Constrains LLM output for narrative drift analysis reports.

**Path:** `.sovereignspec/grammar/drift_report.gbnf`

**Grammar:**
```gbnf
root   ::= "{" ws "\"spec_id\"" ws ":" ws string ws "," ws "\"drift_score\"" ws ":" ws number ws "," ws "\"aligned\"" ws ":" ws boolean ws "," ws "\"constitution_excerpt\"" ws ":" ws string ws "," ws "\"spec_excerpt\"" ws ":" ws string ws "," ws "\"recommendation\"" ws ":" ws string ws "}"
number  ::= "0" "." [0-9] ([0-9])?
boolean ::= "true" | "false"
string  ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws      ::= [ \t\n]*
```

**Example Output:**
```json
{
  "spec_id": "jwt-authentication",
  "drift_score": 0.72,
  "aligned": true,
  "constitution_excerpt": "Build a REST API with TypeScript, Express, and SQLite. No ORM. Functional programming style.",
  "spec_excerpt": "Provide secure JWT-based authentication with access and refresh token flows",
  "recommendation": "Spec is aligned with constitution. Consider adding more functional programming patterns."
}
```

---

## 3. How Grammars Integrate with Ollama

### Non-Streaming Mode

```python
# sovereignspec/engine/grammar.py

import requests
from pathlib import Path

GRAMMAR_DIR = Path(".sovereignspec/grammar")

def load_grammar(name: str) -> str:
    """Load a GBNF grammar file by name (without .gbnf extension)."""
    path = GRAMMAR_DIR / f"{name}.gbnf"
    with open(path) as f:
        return f.read()

def generate_structured(
    prompt: str,
    grammar_name: str,
    model: str = "qwen2.5-coder:32b",
    temperature: float = 0.1
) -> dict:
    """Generate structured output constrained by GBNF grammar.

    Args:
        prompt: The input prompt
        grammar_name: Name of grammar file (without .gbnf)
        model: Ollama model name
        temperature: Sampling temperature (lower = more deterministic)

    Returns:
        Parsed JSON dict matching the grammar's schema
    """
    grammar = load_grammar(grammar_name)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "format": "json",
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 4096,
                "grammar": grammar
            }
        },
        timeout=120
    )

    response.raise_for_status()
    result = response.json()

    # Parse the structured output
    import json
    return json.loads(result["response"])
```

### Streaming Mode

```python
def generate_streaming(
    prompt: str,
    grammar_name: str,
    model: str = "qwen2.5-coder:32b"
):
    """Stream structured output from Ollama with GBNF grammar constraint."""
    grammar = load_grammar(grammar_name)

    with requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.1,
                "grammar": grammar
            }
        },
        stream=True,
        timeout=300
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                import json
                data = json.loads(chunk)
                if "response" in data:
                    yield data["response"]
                if data.get("done"):
                    break
```

### Usage in Spec Compilation

```python
# Example: Generating an implementation plan during spec compile

def generate_implementation_plan(spec: Specification) -> dict:
    """Generate structured implementation plan for a spec."""
    prompt = f"""
    Generate an implementation plan for this specification:

    Spec ID: {spec.id}
    Title: {spec.title}
    Purpose: {spec.purpose}
    Requirements: {', '.join(spec.requirements)}
    Constraints: {', '.join(spec.constraints)}
    Dependencies: {', '.join(spec.dependencies)}

    The project uses TypeScript, Express, and SQLite. No ORM.

    Output a structured implementation plan with files to create/modify.
    """

    return generate_structured(
        prompt=prompt,
        grammar_name="implementation_plan",
        temperature=0.1
    )
```

---

## 4. Writing Custom Grammars

### Tutorial 1: Simple — List of Strings

**Goal:** Constrain output to a JSON array of strings.

```gbnf
root   ::= "[" ws (string (ws "," ws string)*)? ws "]"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws     ::= [ \t\n]*
```

**Usage:** Get the LLM to generate a list of file paths or module names.

### Tutorial 2: Intermediate — Key-Value Pairs

**Goal:** Constrain output to an object with typed fields.

```gbnf
root   ::= "{" ws "\"module_name\"" ws ":" ws string ws "," ws "\"file_count\"" ws ":" ws integer ws "," ws "\"language\"" ws ":" ws string ws "}"
integer ::= [0-9]+
string  ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws      ::= [ \t\n]*
```

**Example Output:** `{"module_name": "src/auth", "file_count": 8, "language": "typescript"}`

### Tutorial 3: Advanced — Nested Objects with Enums

**Goal:** Constrain output to a nested structure with enumerated values.

```gbnf
root        ::= "{" ws "\"status\"" ws ":" ws status ws "," ws "\"checks\"" ws ":" ws checks ws "}"
status      ::= "\"healthy\"" | "\"degraded\"" | "\"unhealthy\""
checks      ::= "[" ws (check (ws "," ws check)*)? ws "]"
check       ::= "{" ws "\"name\"" ws ":" ws string ws "," ws "\"ok\"" ws ":" ws boolean ws "," ws "\"details\"" ws ":" ws string ws "}"
boolean     ::= "true" | "false"
string      ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws          ::= [ \t\n]*
```

**Rules for Writing Effective Grammars:**
1. **Start simple**: Define the root rule first, then build sub-rules
2. **Reuse string and ws**: Always define `string` and `ws` — they are needed for every grammar
3. **Use enums for fixed values**: `"\"" value1 "\"" | "\"" value2 "\""` constrains to specific strings
4. **Limit recursion depth**: Avoid deep recursive rules to keep generation fast
5. **Test with simple prompts**: Verify the grammar produces valid output before using in production
6. **Keep temperature low**: Use 0.1 for deterministic output with grammars
7. **Batch validation**: Output must be exactly valid JSON matching the grammar — validate in code after generation

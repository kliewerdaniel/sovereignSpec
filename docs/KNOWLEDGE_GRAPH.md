# SovereignSpec Knowledge Graph

**Version 1.0.0**

---

## 1. Graph Philosophy: Why Specs Must Be Nodes, Not Documents

Flat markdown files are documents. Documents are passive — you can read them, but they don't know what they relate to. A specification that says "depends on user-profile-api" is just text until a machine can traverse that relationship and answer questions like "what breaks if this changes?".

By modeling each spec as a node in a directed graph, SovereignSpec enables:

- **Impact analysis**: What nodes are affected if a spec changes? Traverse edges to find all descendants.
- **Dependency resolution**: What order must specs be implemented in? Topological sort of DEPENDS_ON edges.
- **Contradiction detection**: Which specs conflict? Find CONFLICTS_WITH edges.
- **Architecture traceability**: Which ADR created this pattern? Follow REFERENCES edges from patterns to ADRs.
- **Drift measurement**: Has a spec drifted from the constitution? Compute through graph-grounded embedding comparison.

The graph is the nervous system of the SovereignSpec project. It connects specs to ADRs, tasks to modules, agents to artifacts. Without the graph, specs are isolated documents. With it, they are a living knowledge base.

---

## 2. Node Type Specifications (11 Types)

### `Project`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `proj-{slug}` |
| `name` | string | Human-readable project name |
| `slug` | string | URL-safe identifier |
| `created_at` | string | ISO 8601 |

**Creation Rule:** Created automatically by `sovereignspec init`.

### `Feature`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `feat-{kebab-name}` |
| `name` | string | Feature name |
| `description` | string | Feature description |
| `status` | string | proposed, planned, in_progress, completed, deferred |

**Creation Rule:** Created by `/sovereign.specify` when the description implies a new user-facing feature.

### `Specification`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `spec-{spec-id}` |
| `title` | string | Spec title |
| `status` | string | Current lifecycle status |
| `version` | string | Semver |
| `file_path` | string | Path to `.sspec` file |

**Creation Rule:** Created by `sovereignspec spec create` or `sovereignspec specify`.

### `Module`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `mod-{path-slug}` |
| `path` | string | File path relative to project root |
| `language` | string | Programming language |
| `type` | string | source, test, config |

**Creation Rule:** Created by `sovereignspec repo map` for every detected source module.

### `Service`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `svc-{name}` |
| `name` | string | Service name |
| `entrypoint` | string | Entrypoint file path |
| `language` | string | Programming language |

**Creation Rule:** Created on spec compilation when the spec describes a deployable service.

### `Endpoint`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `ep-{method}-{path-slug}` |
| `method` | string | HTTP method |
| `path` | string | URL path |
| `auth_required` | boolean | Whether authentication is required |

**Creation Rule:** Created on spec compilation for specs with API endpoints.

### `Database`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `db-{table-name}` |
| `table` | string | Table name |
| `type` | string | table, view, index, migration |

**Creation Rule:** Created on spec compilation for specs with data model definitions.

### `ADR`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `adr-{NNN}` |
| `number` | integer | ADR sequence number |
| `title` | string | ADR title |
| `status` | string | proposed, accepted, deprecated, superseded |

**Creation Rule:** Created by `sovereignspec adr create`.

### `Task`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `task-{uuid}` |
| `title` | string | Task title |
| `status` | string | pending, in_progress, completed, blocked, failed |

**Creation Rule:** Created by `sovereignspec tasks <spec-id>`.

### `Agent`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `agt-{name}` |
| `name` | string | Agent display name |
| `adapter_type` | string | Agent adapter type |
| `last_seen` | string | ISO 8601 |

**Creation Rule:** Created on first agent interaction via artifact submission.

### `Document`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `doc-{path-slug}` |
| `path` | string | File path |
| `type` | string | implementation, testing, api, deployment |

**Creation Rule:** Created by `sovereignspec docs generate`.

---

## 3. Edge Type Specifications (9 Types)

### `IMPLEMENTS`
- **Direction:** Task → Specification
- **Weight:** 1.0 if task is complete, 0.5 if in progress
- **Semantics:** This task implements the spec's requirements
- **Created by:** `sovereignspec tasks <spec-id>`

### `DEPENDS_ON`
- **Direction:** Specification A → Specification B
- **Weight:** 1.0
- **Semantics:** Spec A cannot be implemented before Spec B
- **Created by:** `sovereignspec spec compile` (reads spec dependencies field)

### `REFERENCES`
- **Direction:** Specification → ADR (or Specification → Module)
- **Weight:** 0.5
- **Semantics:** Spec refers to ADR or module for context
- **Created by:** `sovereignspec spec compile` (reads related_adrs field)

### `GENERATES`
- **Direction:** Specification → Document
- **Weight:** 1.0
- **Semantics:** Spec compilation produced this document
- **Created by:** `sovereignspec docs generate`

### `REPLACES`
- **Direction:** Specification A → Specification B
- **Weight:** 1.0
- **Semantics:** New spec replaces old spec (B moves to archived)
- **Created by:** `sovereignspec spec compile --supersedes <old-spec-id>`

### `SUPERSEDES`
- **Direction:** ADR A → ADR B
- **Weight:** 1.0
- **Semantics:** New ADR supersedes old ADR
- **Created by:** `sovereignspec adr create --supersedes <prev-adr>`

### `CONFLICTS_WITH`
- **Direction:** Specification ↔ Specification (bidirectional)
- **Weight:** 0.3-0.9 (higher = more severe conflict)
- **Semantics:** Specs have contradictory requirements
- **Created by:** `sovereignspec analyze --all` (LLM-driven contradiction detection)

### `RELATED_TO`
- **Direction:** Specification ↔ Specification (bidirectional)
- **Weight:** 0.3
- **Semantics:** Specs share context but no hard dependency
- **Created by:** `sovereignspec spec compile` (derived from tag and purpose similarity)

### `VALIDATES`
- **Direction:** Test → Specification
- **Weight:** 1.0
- **Semantics:** Test validates the spec's acceptance criteria
- **Created by:** `sovereignspec implement` (via artifact registration)

---

## 4. graph.json Format Specification

**File:** `.sovereignspec/graph/graph.json`

```json
{
  "$schema": "sovereignspec-graph",
  "project_id": "proj-uuid",
  "updated_at": "2025-01-15T10:00:00Z",
  "nodes": [
    {
      "id": "spec-jwt-authentication",
      "type": "Specification",
      "metadata": {
        "title": "JWT Authentication System",
        "status": "active",
        "version": "1.0.0",
        "file_path": ".sovereignspec/specs/jwt-authentication.sspec"
      }
    },
    {
      "id": "mod-src-auth",
      "type": "Module",
      "metadata": {
        "path": "src/auth",
        "language": "typescript",
        "type": "module"
      }
    },
    {
      "id": "adr-004",
      "type": "ADR",
      "metadata": {
        "number": 4,
        "title": "ChromaDB for Vector Storage",
        "status": "accepted"
      }
    },
    {
      "id": "feat-authentication",
      "type": "Feature",
      "metadata": {
        "name": "Authentication System",
        "status": "in_progress"
      }
    },
    {
      "id": "task-auth-001",
      "type": "Task",
      "metadata": {
        "title": "Create login endpoint",
        "status": "completed"
      }
    },
    {
      "id": "ep-post-auth-login",
      "type": "Endpoint",
      "metadata": {
        "method": "POST",
        "path": "/auth/login",
        "auth_required": false
      }
    },
    {
      "id": "db-refresh-tokens",
      "type": "Database",
      "metadata": {
        "table": "refresh_tokens",
        "type": "table"
      }
    },
    {
      "id": "doc-jwt-auth-implementation",
      "type": "Document",
      "metadata": {
        "path": "docs/jwt-authentication/implementation.md",
        "type": "implementation"
      }
    }
  ],
  "edges": [
    {
      "source": "spec-jwt-authentication",
      "target": "feat-authentication",
      "type": "IMPLEMENTS",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "spec-user-profile-api",
      "type": "DEPENDS_ON",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "adr-004",
      "type": "REFERENCES",
      "weight": 0.5,
      "metadata": {}
    },
    {
      "source": "task-auth-001",
      "target": "spec-jwt-authentication",
      "type": "IMPLEMENTS",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "mod-src-auth",
      "type": "REFERENCES",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "ep-post-auth-login",
      "type": "GENERATES",
      "weight": 1.0,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "db-refresh-tokens",
      "type": "REFERENCES",
      "weight": 0.8,
      "metadata": {}
    },
    {
      "source": "spec-jwt-authentication",
      "target": "doc-jwt-auth-implementation",
      "type": "GENERATES",
      "weight": 1.0,
      "metadata": {}
    }
  ]
}
```

---

## 5. Graph Operations API

### `add_node(id, type, metadata) → node_id`

```python
def add_node(id: str, type: str, metadata: dict = None) -> str:
    """Add a node to the knowledge graph.

    Args:
        id: Unique node identifier (e.g., "spec-jwt-authentication")
        type: Node type from the 11 defined types
        metadata: Arbitrary key-value pairs

    Returns:
        The node ID

    Raises:
        GraphError: If node ID already exists or type is invalid
    """
    validate_node_type(type)
    if id in graph["nodes_by_id"]:
        raise GraphError(f"Node '{id}' already exists")
    node = {"id": id, "type": type, "metadata": metadata or {}}
    graph["nodes"].append(node)
    graph["nodes_by_id"][id] = node
    save_graph()
    return id
```

### `add_edge(source_id, target_id, type, weight, metadata) → edge_id`

```python
def add_edge(source_id: str, target_id: str, type: str,
             weight: float = 1.0, metadata: dict = None) -> str:
    """Add a directed edge between two nodes.

    Args:
        source_id: Source node ID
        target_id: Target node ID
        type: Relationship type from the 9 defined types
        weight: Relationship weight (0.0-1.0)
        metadata: Arbitrary key-value pairs

    Returns:
        The edge identifier

    Raises:
        GraphError: If either node doesn't exist or edge type is invalid
    """
    validate_node_exists(source_id)
    validate_node_exists(target_id)
    validate_edge_type(type)
    edge_id = f"{source_id}→{target_id}::{type}"
    edge = {
        "source": source_id,
        "target": target_id,
        "type": type,
        "weight": max(0.0, min(1.0, weight)),
        "metadata": metadata or {}
    }
    graph["edges"].append(edge)
    save_graph()
    return edge_id
```

### `what_breaks_if_changed(spec_id) → list[Node]`

```python
def what_breaks_if_changed(spec_id: str, max_depth: int = 3) -> list[Node]:
    """Find all nodes that would be affected if this spec changes.

    Traverses outgoing edges (DEPENDS_ON reversed, REFERENCES, GENERATES)
    up to max_depth. Returns all descendants sorted by distance.

    Args:
        spec_id: Specification node ID
        max_depth: Maximum graph traversal depth (default: 3)

    Returns:
        List of affected nodes with distance annotations
    """
    visited = set()
    queue = [(spec_id, 0)]
    affected = []

    while queue:
        current_id, depth = queue.pop(0)
        if current_id in visited or depth > max_depth:
            continue
        visited.add(current_id)

        # Find all nodes that depend on current_id
        # (incoming DEPENDS_ON edges)
        for edge in graph["edges"]:
            if edge["type"] == "DEPENDS_ON" and edge["target"] == current_id:
                source_node = graph["nodes_by_id"].get(edge["source"])
                if source_node and source_node["id"] not in visited:
                    affected.append(source_node)
                    queue.append((source_node["id"], depth + 1))

            # Find all nodes that reference current_id
            if edge["type"] == "REFERENCES" and edge["target"] == current_id:
                source_node = graph["nodes_by_id"].get(edge["source"])
                if source_node and source_node["id"] not in visited:
                    affected.append(source_node)
                    queue.append((source_node["id"], depth + 1))

            # Find generated docs
            if edge["type"] == "GENERATES" and edge["source"] == current_id:
                target_node = graph["nodes_by_id"].get(edge["target"])
                if target_node:
                    affected.append(target_node)

    return affected
```

### `what_specs_affect_module(module_path) → list[Specification]`

```python
def what_specs_affect_module(module_path: str) -> list[Node]:
    """Find all specs that reference a given module path.

    Args:
        module_path: Module file path (e.g., "src/auth/jwt.ts")

    Returns:
        List of Specification nodes that REFERENCE this module
    """
    module_id = f"mod-{module_path.replace('/', '-').replace('.', '-')}"
    affecting_specs = []

    for edge in graph["edges"]:
        if (edge["type"] == "REFERENCES"
            and edge["target"] == module_id):
            source = graph["nodes_by_id"].get(edge["source"])
            if source and source["type"] == "Specification":
                affecting_specs.append(source)

    return affecting_specs
```

### `which_adr_created_architecture(pattern) → list[ADR]`

```python
def which_adr_created_architecture(pattern_name: str) -> list[Node]:
    """Find ADRs that resulted in a specific architectural pattern.

    Searches by matching pattern name against node metadata and
    traversing REFERENCES edges from ADRs to specifications.

    Args:
        pattern_name: Name of the architectural pattern

    Returns:
        List of ADR nodes associated with this pattern
    """
    matching_adrs = set()

    # Search ADR metadata for pattern name
    for node in graph["nodes"]:
        if node["type"] == "ADR":
            if pattern_name.lower() in str(node["metadata"]).lower():
                matching_adrs.add(node["id"])

    # Search for specs that reference this pattern, then find their ADRs
    for edge in graph["edges"]:
        if edge["type"] == "REFERENCES" and edge["target"].startswith("adr-"):
            source = graph["nodes_by_id"].get(edge["source"])
            if source and source["type"] == "Specification":
                if pattern_name.lower() in str(source["metadata"]).lower():
                    matching_adrs.add(edge["target"])

    return [graph["nodes_by_id"][aid] for aid in matching_adrs]
```

### `dependency_chain(spec_id, depth) → Tree`

```python
def dependency_chain(spec_id: str, max_depth: int = 5) -> dict:
    """Return the full dependency tree for a spec.

    Traverses DEPENDS_ON edges to build a nested dependency tree.

    Args:
        spec_id: Specification node ID
        max_depth: Maximum recursion depth

    Returns:
        Nested dict representing the dependency tree
    """
    def _build_chain(node_id: str, remaining_depth: int) -> dict:
        if remaining_depth <= 0:
            return {"id": node_id, "dependencies": []}

        deps = []
        for edge in graph["edges"]:
            if (edge["type"] == "DEPENDS_ON"
                and edge["source"] == node_id):
                dep_chain = _build_chain(edge["target"], remaining_depth - 1)
                deps.append(dep_chain)

        return {"id": node_id, "dependencies": deps}

    return _build_chain(spec_id, max_depth)
```

### `find_contradictions() → list[ContradictionPair]`

```python
from dataclasses import dataclass

@dataclass
class ContradictionPair:
    spec_a: str
    spec_b: str
    score: float
    description: str
    affected_fields: list[str]

def find_contradictions() -> list[ContradictionPair]:
    """Find all CONFLICTS_WITH edges in the graph.

    Returns:
        List of ContradictionPair objects
    """
    contradictions = []
    for edge in graph["edges"]:
        if edge["type"] == "CONFLICTS_WITH":
            contradictions.append(ContradictionPair(
                spec_a=edge["source"],
                spec_b=edge["target"],
                score=edge["weight"],
                description=edge["metadata"].get("description", ""),
                affected_fields=edge["metadata"].get("affected_fields", [])
            ))
    return contradictions
```

### `compute_drift_score(spec_id) → float`

```python
def compute_drift_score(spec_id: str, constitution_text: str,
                        chroma: ChromaClient, ollama: OllamaClient) -> float:
    """Compute narrative drift score for a spec.

    Embeds the spec and constitution, computes cosine similarity.
    1.0 = perfectly aligned, 0.0 = completely drifted.

    Args:
        spec_id: Specification node ID
        constitution_text: Full text of constitution.md
        chroma: ChromaDB client instance
        ollama: Ollama client instance

    Returns:
        Drift score (0.0-1.0)
    """
    spec = graph["nodes_by_id"].get(spec_id)
    if not spec:
        raise GraphError(f"Spec '{spec_id}' not found")

    spec_text = f"{spec['metadata'].get('title', '')} {spec['metadata'].get('purpose', '')}"

    spec_embedding = ollama.embed(spec_text)
    constitution_embedding = ollama.embed(constitution_text)

    similarity = cosine_similarity(spec_embedding, constitution_embedding)
    return max(0.0, similarity)
```

---

## 6. Contradiction Detection Algorithm

```python
"""
Contradiction Detection Algorithm
==================================

Phase 1: Candidate Identification
  For each active spec in the project:
    1. Embed the spec's requirements + constraints + acceptance criteria
       using the embeddings model (nomic-embed-text)
    2. Query ChromaDB for the top-10 most similar specs (by cosine similarity)
    3. Filter out the spec itself and already-known pairs
    4. These are candidate contradiction pairs

Phase 2: LLM Analysis with GBNF Constraint
  For each candidate pair (spec_a, spec_b):
    1. Construct a prompt that asks "Do these specs have contradictory requirements?"
    2. Include:
       - spec_a's requirements + constraints + acceptance criteria
       - spec_b's requirements + constraints + acceptance criteria
    3. Constrain output with contradiction_report.gbnf grammar
    4. Parse the LLM response:
       {
         "contradiction_score": 0.0-1.0,  // LLM-estimated contradiction likelihood
         "contradiction": boolean,         // true if score >= 0.7
         "description": string,            // explanation of the contradiction
         "affected_fields": [string]       // which fields/requirements conflict
       }

Phase 3: Graph Integration
  For each confirmed contradiction (contradiction == true):
    1. Add CONFLICTS_WITH edge between spec_a and spec_b
       - Weight = contradiction_score (0.7-1.0)
       - Metadata includes description and affected_fields
    2. Store in spec_relationships SQLite table
    3. Log to analysis report

Phase 4: Cross-Validation
  For confirmed contradictions:
    1. Check if the contradiction affects acceptance criteria
    2. If yes, flag both specs for human review
    3. If the contradiction is in optional or non-functional areas,
       add to the analysis report without blocking compilation

Complexity: O(n * m) where n = number of active specs, m = ChromaDB results per spec
"""
```

---

## 7. Narrative Drift Tracking Algorithm

```python
"""
Narrative Drift Tracking Algorithm
===================================

Phase 1: Constitution Embedding (one-time, on sovereign-constitution)
  1. Load .sovereignspec/constitution.md
  2. Compute embedding via Ollama embeddings model
  3. Store as "constitution_vector" in SQLite project metadata
  4. This is the baseline vector against which all specs are scored

Phase 2: Spec Scoring (on every spec compile)
  For each compiled spec:
    1. Load spec content (purpose + requirements + constraints)
    2. Compute embedding via Ollama embeddings model
    3. Retrieve constitution vector from SQLite
    4. Compute cosine similarity:
       drift_score = cosine_similarity(spec_vector, constitution_vector)
    5. Normalize to [0.0, 1.0]:
       - 1.0 = spec perfectly aligns with constitution
       - 0.0 = spec completely contradicts constitution
    6. Store in spec_versions.drift_score

Phase 3: Threshold Check
  If drift_score < 0.6:
    - Flag spec for human review
    - Include in analysis report
    - Extract constitution section that relates to the drifted requirement:
      * Find the constitution sentence/paragraph with highest similarity
        to the drifted spec requirement
      * Include as "Recommended alignment target"
    - Do NOT block compilation (drift is advisory, not blocking)

Phase 4: Trend Analysis (on sovereignspec analyze --all)
  For each spec with multiple versions:
    1. Retrieve all drift scores across versions
    2. Compute drift velocity:
       velocity = (current_score - previous_score) / time_delta
    3. If velocity < -0.1 per week (score decreasing faster than 0.1/week):
       Flag as "accelerating drift"
    4. If velocity > 0.05 per week (score increasing):
       Flag as "recovering alignment"

Phase 5: Aggregate Scoring (on sovereignspec analyze --all)
  Project-level drift metrics:
    - Mean drift score across all active specs
    - Minimum drift score (most drifted spec)
    - Drift distribution (how many specs in each band: 0.0-0.3, 0.3-0.6, 0.6-0.8, 0.8-1.0)
    - Trending: is the project as a whole drifting?
"""

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = sum(a * a for a in v1) ** 0.5
    magnitude_v2 = sum(b * b for b in v2) ** 0.5
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0.0
    return dot_product / (magnitude_v1 * magnitude_v2)
```

---

## 8. Neo4j Upgrade Guide

To upgrade from adjacency JSON to Neo4j:

1. Install Neo4j (local or Docker):
   ```bash
   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 neo4j:5
   ```

2. Update `.sovereignspec/config.json`:
   ```json
   {
     "graph": {
       "store": "neo4j",
       "neo4j": {
         "uri": "bolt://localhost:7687",
         "user": "neo4j",
         "password": "env:NEO4J_PASSWORD"
       }
     }
   }
   ```

3. Run migration:
   ```bash
   sovereignspec memory sync --rebuild-graph
   ```

### Cypher Query Equivalents

| Adjacency JSON | Cypher |
|----------------|--------|
| `add_node(id, type, metadata)` | `CREATE (n:Node {id: $id}) SET n += $metadata, n.type = $type` |
| `add_edge(source, target, type, weight)` | `MATCH (s {id: $src}), (t {id: $tgt}) CREATE (s)-[r:REL {type: $type, weight: $weight}]->(t)` |
| `what_breaks_if_changed(id)` | `MATCH (s {id: $id})<-[*1..3]-(affected) RETURN affected` |
| `dependency_chain(id)` | `MATCH path=(s {id: $id})-[:DEPENDS_ON*]->(deps) RETURN path` |
| `find_contradictions()` | `MATCH (a)-[r:CONFLICTS_WITH]->(b) RETURN a.id, b.id, r.weight, r.description` |
| `what_specs_affect_module(path)` | `MATCH (s:Specification)-[:REFERENCES]->(m:Module {path: $path}) RETURN s` |

---

## 9. Graph Query Examples

### Example: Impact Analysis

```bash
sovereignspec graph query --what-breaks spec-jwt-authentication
```

**Expected Output:**
```
What breaks if spec:jwt-authentication changes:
  Depth 1:
    - spec:user-profile-api (DEPENDS_ON)
    - feat:authentication-system (IMPLEMENTS by task)
  Depth 2:
    - mod:src/auth/middleware.ts (REFERENCES from jwt-authentication)
    - task:auth-003-verify-token (IMPLEMENTS spec:jwt-authentication)
  Depth 3:
    - doc:jwt-authentication-implementation (GENERATED by spec)
    - spec:rate-limiting (REFERENCES shared module)
```

### Example: Module Traceability

```bash
sovereignspec graph query --affects-module src/auth/middleware.ts
```

**Expected Output:**
```
Specs that reference src/auth/middleware.ts:
  - spec:jwt-authentication (REFERENCES)
  - spec:rate-limiting (REFERENCES - uses same middleware chain)
  - spec:user-profile-api (REFERENCES - depends on auth middleware)

ADRs that influenced these specs:
  - ADR-004: ChromaDB for Vector Storage
  - ADR-006: SQLite as Primary Metadata Store
```

### Example: Dependency Chain

```python
from sovereignspec.engine.graph import KnowledgeGraph

kg = KnowledgeGraph(".sovereignspec/graph/graph.json")
chain = kg.dependency_chain("spec-api-gateway", max_depth=4)
print(json.dumps(chain, indent=2))
```

**Output:**
```json
{
  "id": "spec-api-gateway",
  "dependencies": [
    {
      "id": "spec-rate-limiting",
      "dependencies": []
    },
    {
      "id": "spec-jwt-authentication",
      "dependencies": [
        {
          "id": "spec-user-profile-api",
          "dependencies": []
        }
      ]
    }
  ]
}
```

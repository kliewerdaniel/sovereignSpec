#!/usr/bin/env python3
"""Verify documentation matches implementation.

Usage: python scripts/verify_docs.py
Exit code: 0 if all checks pass, 1 if any discrepancies found.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GBNF_DIR = ROOT / ".sovereignspec" / "grammar"
DOCS_DIR = ROOT / "docs"

errors: list[str] = []


def check(condition: bool, msg: str) -> None:
    if not condition:
        errors.append(msg)


def read_doc(path: str) -> str:
    return (DOCS_DIR / path).read_text()


def read_source(path: str) -> str:
    return (ROOT / "sovereignspec" / path).read_text()


# --- 1. GBNF Grammars ---
def check_grammars() -> None:
    claimed = [
        "spec_validation_result", "implementation_plan", "task_list",
        "api_spec", "adr", "test_case", "contradiction_report", "drift_report",
    ]
    actual = {f.stem for f in GBNF_DIR.glob("*.gbnf")}
    for name in claimed:
        check(
            name in actual,
            f"Grammar '{name}.gbnf' documented but not found in {GBNF_DIR}",
        )


# --- 2. CLI Commands ---
def check_cli_commands() -> None:
    main_source = read_source("cli/main.py")
    tree = ast.parse(main_source)
    actual_commands: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    actual_commands.add(key.value)

    cli_doc = read_doc("CLI_REFERENCE.md")
    claimed_commands = ["init", "doctor", "spec", "sovereign-constitution",
                         "specify", "clarify", "plan", "tasks", "analyze",
                         "implement", "graph", "context", "adr", "memory",
                         "repo", "docs"]

    for cmd in claimed_commands:
        pattern = rf"sovereignspec {cmd}\b|`{cmd}`"
        check(
            re.search(pattern, cli_doc, re.I),
            f"CLI command '{cmd}' not found in CLI_REFERENCE.md",
        )
        check(
            cmd in actual_commands,
            f"CLI command '{cmd}' in docs but not in _COMMANDS dict",
        )

    # Check exit codes are present
    doc_exit = read_doc("CLI_REFERENCE.md")
    for code in range(6):
        check(
            f"| {code} |" in doc_exit,
            f"Exit code {code} not documented in exit code table",
        )


# --- 3. Validation Error Codes ---
def check_validation_codes() -> None:
    validator_source = read_source("engine/validator.py")
    actual_codes = set(re.findall(r'code="([A-Z_]+)"', validator_source))

    doc_cli = read_doc("CLI_REFERENCE.md")
    doc_spec = read_doc("SPECIFICATION_FORMAT.md")
    combined_doc = doc_cli + "\n" + doc_spec
    documented_codes = set(re.findall(r'`([A-Z_]+)`', combined_doc))

    for code in actual_codes:
        check(
            code in combined_doc,
            f"Validation error code '{code}' exists in code but not in any doc",
        )


# --- 4. Spec Fields ---
def check_spec_fields() -> None:
    spec_source = read_source("models/spec.py")
    tree = ast.parse(spec_source)
    actual_fields: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Specification":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    actual_fields.add(item.target.id)

    spec_doc = read_doc("SPECIFICATION_FORMAT.md")
    claimed_fields = [
        "id", "title", "version", "status", "purpose",
        "requirements", "constraints", "acceptance_criteria",
        "dependencies", "test_cases", "security_requirements",
        "performance_requirements", "architecture_notes",
        "implementation_hints", "tags",
    ]
    for field in claimed_fields:
        check(
            field in actual_fields,
            f"Spec field '{field}' documented but not in Specification model",
        )


# --- 5. Node/Edge Types ---
def check_graph_types() -> None:
    graph_source = read_source("models/graph.py")
    tree = ast.parse(graph_source)

    actual_nodes: set[str] = set()
    actual_edges: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == "NodeType":
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for t in item.targets:
                            if isinstance(t, ast.Name):
                                actual_nodes.add(t.id)
            elif node.name == "EdgeType":
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for t in item.targets:
                            if isinstance(t, ast.Name):
                                actual_edges.add(t.id)

    kg_doc = read_doc("KNOWLEDGE_GRAPH.md")
    display_names = {
        "PROJECT": "Project", "FEATURE": "Feature", "SPECIFICATION": "Specification",
        "MODULE": "Module", "SERVICE": "Service", "ENDPOINT": "Endpoint",
        "DATABASE": "Database", "ADR": "ADR", "TASK": "Task",
        "AGENT": "Agent", "DOCUMENT": "Document",
    }
    for enum_name, display_name in display_names.items():
        check(
            display_name in kg_doc or f"`{display_name}`" in kg_doc,
            f"Node type '{enum_name}' ({display_name}) not documented in KNOWLEDGE_GRAPH.md",
        )

    edge_display = {
        "IMPLEMENTS": "IMPLEMENTS", "DEPENDS_ON": "DEPENDS_ON",
        "REFERENCES": "REFERENCES", "GENERATES": "GENERATES",
        "REPLACES": "REPLACES", "SUPERSEDES": "SUPERSEDES",
        "CONFLICTS_WITH": "CONFLICTS_WITH", "RELATED_TO": "RELATED_TO",
        "VALIDATES": "VALIDATES",
    }
    for enum_name, display_name in edge_display.items():
        check(
            display_name in kg_doc or f"`{display_name}`" in kg_doc,
            f"Edge type '{enum_name}' not documented in KNOWLEDGE_GRAPH.md",
        )


# --- 6. Agent Adapters ---
def check_adapters() -> None:
    adapters_dir = ROOT / "sovereignspec" / "adapters"
    adapter_files = {f.stem for f in adapters_dir.glob("*.py") if f.stem not in ("__init__", "base")}

    agent_doc = read_doc("AGENT_INTEGRATION.md")
    for name in adapter_files:
        display_name = name.replace("_", "-").replace("continue-", "continue")
        check(
            display_name.replace("-", " ") in agent_doc.lower() or display_name in agent_doc,
            f"Adapter '{name}' exists in code but not documented in AGENT_INTEGRATION.md",
        )


def main() -> None:
    check_grammars()
    check_cli_commands()
    check_validation_codes()
    check_spec_fields()
    check_graph_types()
    check_adapters()

    if errors:
        print(f"Found {len(errors)} documentation discrepancies:\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("All documentation checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()

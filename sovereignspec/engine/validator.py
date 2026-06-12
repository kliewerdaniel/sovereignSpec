from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from sovereignspec.models.spec import SpecStatus, Specification
from sovereignspec.models.graph import KnowledgeGraph


@dataclass
class ValidationContext:
    db: Any = None
    graph: KnowledgeGraph | None = None
    llm: Any = None
    constitution_text: str = ""
    all_specs: dict[str, Specification] = field(default_factory=dict)
    existing_statuses: dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationError:
    code: str
    message: str
    spec_id: str


ValidationRule = Callable[[Specification, ValidationContext], list[ValidationError]]


class Validator:
    def __init__(self) -> None:
        self._rules: list[ValidationRule] = []

    def register(self, rule: ValidationRule) -> None:
        self._rules.append(rule)

    def validate(self, spec: Specification, context: ValidationContext) -> list[ValidationError]:
        errors: list[ValidationError] = []
        for rule in self._rules:
            errors.extend(rule(spec, context))
        return errors

    def validate_all(self, context: ValidationContext) -> dict[str, list[ValidationError]]:
        results: dict[str, list[ValidationError]] = {}
        for spec_id, spec in context.all_specs.items():
            results[spec_id] = self.validate(spec, context)
        return results


def _rule_missing_purpose(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if not spec.purpose or not spec.purpose.strip():
        return [ValidationError(
            code="MISSING_PURPOSE",
            message=f"Spec '{spec.id}' is missing a purpose. Every spec must describe what it accomplishes.",
            spec_id=spec.id,
        )]
    return []


def _rule_ambiguous_requirements(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for req in spec.requirements:
        if not re.search(r"\b(must|shall|should|will)\b", req, re.IGNORECASE):
            errors.append(ValidationError(
                code="AMBIGUOUS_REQUIREMENTS",
                message=f"Requirement '{req}' in spec '{spec.id}' is ambiguous. Use format: 'System must [action] [object] [condition]'.",
                spec_id=spec.id,
            ))
    return errors


def _rule_undefined_dependency(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for dep_id in spec.dependencies:
        if dep_id not in ctx.all_specs:
            errors.append(ValidationError(
                code="UNDEFINED_DEPENDENCY",
                message=f"Spec '{spec.id}' depends on '{dep_id}', but no spec with that ID exists.",
                spec_id=spec.id,
            ))
    return errors


def _rule_missing_acceptance_criteria(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if not spec.acceptance_criteria:
        return [ValidationError(
            code="MISSING_ACCEPTANCE_CRITERIA",
            message=f"Spec '{spec.id}' is missing acceptance criteria. Every spec must define how to verify correct implementation.",
            spec_id=spec.id,
        )]
    return []


def _rule_missing_test_cases(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if not spec.test_cases:
        return [ValidationError(
            code="MISSING_TEST_CASES",
            message=f"Spec '{spec.id}' is missing test cases. Every spec must define at least one test case.",
            spec_id=spec.id,
        )]
    return []


def _rule_dependency_cycle(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if ctx.graph:
        try:
            ctx.graph.topological_sort()
        except ValueError as e:
            return [ValidationError(
                code="DEPENDENCY_CYCLE",
                message=f"Circular dependency detected: {e}",
                spec_id=spec.id,
            )]
    return []


def _rule_duplicate_id(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if ctx.existing_statuses.get(spec.id):
        return [ValidationError(
            code="DUPLICATE_ID",
            message=f"A spec with ID '{spec.id}' already exists. Choose a different ID or use versioning.",
            spec_id=spec.id,
        )]
    return []


def _rule_incomplete_security(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    combined = (spec.purpose + " " + " ".join(spec.requirements) + " " + " ".join(spec.constraints)).lower()
    sensitive_terms = {"auth", "authentication", "authorization", "password", "pii", "token", "credential", "login"}
    if any(t in combined for t in sensitive_terms) and not spec.security_requirements:
        return [ValidationError(
            code="INCOMPLETE_SECURITY",
            message=f"Spec '{spec.id}' involves authentication/authorization or sensitive data but has no security requirements defined.",
            spec_id=spec.id,
        )]
    return []


_VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"validated"},
    "validated": {"approved"},
    "approved": {"active"},
    "active": {"implemented", "archived"},
    "implemented": {"verified"},
    "verified": {"archived"},
    "archived": {"active"},
}


def _rule_invalid_status_transition(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    current = ctx.existing_statuses.get(spec.id)
    if current and current in _VALID_TRANSITIONS:
        if spec.status.value not in _VALID_TRANSITIONS[current]:
            valid = ", ".join(sorted(_VALID_TRANSITIONS[current]))
            return [ValidationError(
                code="INVALID_STATUS_TRANSITION",
                message=f"Cannot transition spec '{spec.id}' from '{current}' to '{spec.status.value}'. Valid transitions: {valid}",
                spec_id=spec.id,
            )]
    return []


def _rule_missing_constraints(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if not spec.constraints:
        return [ValidationError(
            code="MISSING_CONSTRAINTS",
            message=f"Spec '{spec.id}' has no constraints. Every spec must define at least one hard constraint.",
            spec_id=spec.id,
        )]
    return []


def _rule_narrative_drift(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if ctx.llm and ctx.constitution_text:
        from sovereignspec.engine.drift import DriftTracker
        tracker = DriftTracker(ctx.llm, ctx.constitution_text)
        report = tracker.compute_drift(spec)
        if report.drift_score < 0.6:
            excerpt = ctx.constitution_text[:100].replace("\n", " ")
            return [ValidationError(
                code="NARRATIVE_DRIFT",
                message=f"Spec '{spec.id}' has drifted from the project constitution (score: {report.drift_score:.2f}). Consider revising to align with: '{excerpt}...'",
                spec_id=spec.id,
            )]
    return []


def _rule_contradicts_existing_spec(spec: Specification, ctx: ValidationContext) -> list[ValidationError]:
    if ctx.llm and ctx.graph:
        from sovereignspec.engine.contradiction import ContradictionDetector
        detector = ContradictionDetector(ctx.llm, ctx.graph, None)
        pairs = detector.detect(spec.id)
        for pair in pairs:
            if pair.score >= 0.7:
                return [ValidationError(
                    code="CONTRADICTS_EXISTING_SPEC",
                    message=f"Spec '{spec.id}' contradicts '{pair.spec_b}' (score: {pair.score:.2f}). Details: {pair.description}",
                    spec_id=spec.id,
                )]
    return []


def create_default_validator() -> Validator:
    v = Validator()
    v.register(_rule_missing_purpose)
    v.register(_rule_ambiguous_requirements)
    v.register(_rule_undefined_dependency)
    v.register(_rule_missing_acceptance_criteria)
    v.register(_rule_missing_test_cases)
    v.register(_rule_dependency_cycle)
    v.register(_rule_duplicate_id)
    v.register(_rule_incomplete_security)
    v.register(_rule_invalid_status_transition)
    v.register(_rule_missing_constraints)
    v.register(_rule_narrative_drift)
    v.register(_rule_contradicts_existing_spec)
    return v

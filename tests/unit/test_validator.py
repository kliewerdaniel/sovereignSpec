from __future__ import annotations

import pytest

from sovereignspec.engine.validator import (
    ValidationContext,
    Validator,
    _rule_ambiguous_requirements,
    _rule_duplicate_id,
    _rule_incomplete_security,
    _rule_missing_acceptance_criteria,
    _rule_missing_constraints,
    _rule_missing_purpose,
    _rule_missing_test_cases,
    _rule_undefined_dependency,
    create_default_validator,
)
from sovereignspec.models.spec import Specification


@pytest.fixture
def validator() -> Validator:
    return create_default_validator()


@pytest.fixture
def valid_spec() -> Specification:
    return Specification(
        id="valid-spec",
        title="Valid Spec",
        purpose="A valid specification for testing",
        requirements=["System must authenticate users"],
        constraints=["No external dependencies"],
        acceptance_criteria=["Login returns token"],
        test_cases=[{"id": "T-1", "description": "Login works", "given": "valid creds", "when": "login", "then": "token"}],
        dependencies=[],
    )


@pytest.fixture
def context() -> ValidationContext:
    return ValidationContext(
        all_specs={"valid-spec": Specification(id="valid-spec", title="Existing", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])},
    )


class TestMissingPurpose:
    def test_fails_when_empty(self) -> None:
        spec = Specification(id="x", title="x", purpose="", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_missing_purpose(spec, ValidationContext())
        assert len(errors) == 1
        assert errors[0].code == "MISSING_PURPOSE"

    def test_passes_when_present(self, valid_spec: Specification) -> None:
        errors = _rule_missing_purpose(valid_spec, ValidationContext())
        assert len(errors) == 0


class TestMissingAcceptanceCriteria:
    def test_fails_when_empty(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["req"], constraints=["c"], acceptance_criteria=[], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_missing_acceptance_criteria(spec, ValidationContext())
        assert len(errors) == 1
        assert errors[0].code == "MISSING_ACCEPTANCE_CRITERIA"

    def test_passes_when_present(self, valid_spec: Specification) -> None:
        errors = _rule_missing_acceptance_criteria(valid_spec, ValidationContext())
        assert len(errors) == 0


class TestMissingTestCases:
    def test_fails_when_empty(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[])
        errors = _rule_missing_test_cases(spec, ValidationContext())
        assert len(errors) == 1
        assert errors[0].code == "MISSING_TEST_CASES"


class TestMissingConstraints:
    def test_fails_when_empty(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["req"], constraints=[], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_missing_constraints(spec, ValidationContext())
        assert len(errors) == 1
        assert errors[0].code == "MISSING_CONSTRAINTS"


class TestAmbiguousRequirements:
    def test_fails_without_action_verb(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["Handle user input"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_ambiguous_requirements(spec, ValidationContext())
        assert len(errors) == 1

    def test_passes_with_action_verb(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["System must handle user input"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_ambiguous_requirements(spec, ValidationContext())
        assert len(errors) == 0


class TestUndefinedDependency:
    def test_fails_on_undefined_dep(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["r"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}], dependencies=["missing-dep"])
        ctx = ValidationContext(all_specs={})
        errors = _rule_undefined_dependency(spec, ctx)
        assert len(errors) == 1

    def test_passes_when_dep_exists(self) -> None:
        spec = Specification(id="x", title="x", purpose="p", requirements=["r"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}], dependencies=["existing-dep"])
        ctx = ValidationContext(all_specs={"existing-dep": spec})
        errors = _rule_undefined_dependency(spec, ctx)
        assert len(errors) == 0


class TestDuplicateId:
    def test_fails_on_duplicate(self) -> None:
        spec = Specification(id="dup", title="x", purpose="p", requirements=["r"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        ctx = ValidationContext(existing_statuses={"dup": "draft"})
        errors = _rule_duplicate_id(spec, ctx)
        assert len(errors) == 1

    def test_passes_on_new_id(self, valid_spec: Specification) -> None:
        ctx = ValidationContext(existing_statuses={})
        errors = _rule_duplicate_id(valid_spec, ctx)
        assert len(errors) == 0


class TestIncompleteSecurity:
    def test_fails_for_auth_spec_without_security(self) -> None:
        spec = Specification(id="x", title="x", purpose="Authentication service", requirements=["System must authenticate"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        errors = _rule_incomplete_security(spec, ValidationContext())
        assert len(errors) == 1

    def test_passes_with_security(self) -> None:
        spec = Specification(id="x", title="x", purpose="Authentication service", requirements=["System must authenticate"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}], security_requirements=["Use JWT"])
        errors = _rule_incomplete_security(spec, ValidationContext())
        assert len(errors) == 0


class TestValidatorFull:
    def test_valid_spec_passes_all(self, validator: Validator, valid_spec: Specification, context: ValidationContext) -> None:
        errors = validator.validate(valid_spec, context)
        codes = {e.code for e in errors}
        assert "MISSING_PURPOSE" not in codes
        assert "MISSING_ACCEPTANCE_CRITERIA" not in codes
        assert "MISSING_TEST_CASES" not in codes
        assert "MISSING_CONSTRAINTS" not in codes

    def test_invalid_spec_fails_multiple(self, validator: Validator) -> None:
        spec = Specification(id="bad", title="Bad", purpose="", requirements=["bad req"], constraints=[], acceptance_criteria=[], test_cases=[])
        ctx = ValidationContext()
        errors = validator.validate(spec, ctx)
        codes = {e.code for e in errors}
        assert "MISSING_PURPOSE" in codes
        assert "MISSING_ACCEPTANCE_CRITERIA" in codes
        assert "MISSING_TEST_CASES" in codes
        assert "MISSING_CONSTRAINTS" in codes

    def test_validate_all(self, validator: Validator) -> None:
        spec1 = Specification(id="s1", title="S1", purpose="p", requirements=["System must do r"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        spec2 = Specification(id="s2", title="S2", purpose="", requirements=["System must do r"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        ctx = ValidationContext(all_specs={"s1": spec1, "s2": spec2})
        results = validator.validate_all(ctx)
        assert len(results["s1"]) == 0
        assert any(e.code == "MISSING_PURPOSE" for e in results["s2"])

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sovereignspec.models.spec import Specification, SpecStatus, TestCase


class TestSpecificationModel:
    def test_create_valid_spec(self, sample_spec: Specification) -> None:
        assert sample_spec.id == "test-auth"
        assert sample_spec.title == "Test Authentication"
        assert sample_spec.status == SpecStatus.DRAFT
        assert len(sample_spec.requirements) == 2
        assert len(sample_spec.test_cases) == 1

    def test_kebab_case_id_valid(self) -> None:
        spec = Specification(id="valid-kebab-id", title="Test", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        assert spec.id == "valid-kebab-id"

    def test_kebab_case_id_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Specification(id="Invalid_ID", title="Test", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])

    def test_semver_version_valid(self) -> None:
        spec = Specification(id="test", title="Test", version="2.1.3", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        assert spec.version == "2.1.3"

    def test_semver_version_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Specification(id="test", title="Test", version="abc", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])

    def test_yaml_round_trip(self, sample_spec: Specification) -> None:
        yaml_str = sample_spec.to_yaml()
        parsed = Specification.from_yaml(yaml_str)
        assert parsed.id == sample_spec.id
        assert parsed.title == sample_spec.title
        assert parsed.status == sample_spec.status
        assert len(parsed.requirements) == len(sample_spec.requirements)

    def test_yaml_round_trip_with_test_cases(self) -> None:
        spec = Specification(
            id="test-with-cases",
            title="Test Cases",
            requirements=["req"],
            constraints=["c"],
            acceptance_criteria=["ac"],
            test_cases=[
                TestCase(id="TC-1", description="First", given="given", when="when", then="then"),
            ],
        )
        yaml_str = spec.to_yaml()
        parsed = Specification.from_yaml(yaml_str)
        assert len(parsed.test_cases) == 1
        assert parsed.test_cases[0].id == "TC-1"

    def test_checksum_stable(self, sample_spec: Specification) -> None:
        cs1 = sample_spec.checksum()
        cs2 = sample_spec.checksum()
        assert cs1 == cs2

    def test_checksum_changes_on_modification(self, sample_spec: Specification) -> None:
        cs1 = sample_spec.checksum()
        sample_spec.title = "Modified Title"
        cs2 = sample_spec.checksum()
        assert cs1 != cs2

    def test_default_status_is_draft(self) -> None:
        spec = Specification(id="new-spec", title="New", requirements=["req"], constraints=["c"], acceptance_criteria=["ac"], test_cases=[{"id": "T-1", "description": "test"}])
        assert spec.status == SpecStatus.DRAFT

    def test_empty_yaml_raises_error(self) -> None:
        with pytest.raises(ValueError):
            Specification.from_yaml("")

    def test_null_yaml_raises_error(self) -> None:
        with pytest.raises(ValueError):
            Specification.from_yaml("null")

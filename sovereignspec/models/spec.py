from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class SpecStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    ACTIVE = "active"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    ARCHIVED = "archived"


class SpecValidationError(BaseModel):
    code: str
    message: str
    spec_id: str


class TestCase(BaseModel):
    id: str
    description: str
    given: str = ""
    when: str = ""
    then: str = ""


class PerformanceRequirement(BaseModel):
    metric: str
    threshold: str


class Specification(BaseModel):
    id: str
    title: str
    version: str = "1.0.0"
    status: SpecStatus = SpecStatus.DRAFT
    purpose: str = ""
    requirements: list[str] = []
    constraints: list[str] = []
    acceptance_criteria: list[str] = []
    dependencies: list[str] = []
    test_cases: list[TestCase] = []
    security_requirements: list[str] = []
    performance_requirements: list[PerformanceRequirement] = []
    architecture_notes: str = ""
    implementation_hints: list[str] = []
    non_functional_requirements: list[str] = []
    related_adrs: list[str] = []
    tags: list[str] = []

    @field_validator("id")
    @classmethod
    def id_must_be_kebab_case(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", v):
            raise ValueError("id must be kebab-case (e.g. 'jwt-authentication')")
        return v

    @field_validator("version")
    @classmethod
    def version_must_be_semver(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("version must be semver (e.g. '1.0.0')")
        return v

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v

    @field_validator("requirements")
    @classmethod
    def requirements_must_not_be_empty(cls, v: list[str]) -> list[str]:
        return v if v else []

    @field_validator("constraints")
    @classmethod
    def constraints_must_not_be_empty(cls, v: list[str]) -> list[str]:
        return v if v else []

    @field_validator("acceptance_criteria")
    @classmethod
    def acceptance_criteria_must_not_be_empty(cls, v: list[str]) -> list[str]:
        return v if v else []

    @field_validator("test_cases")
    @classmethod
    def test_cases_must_not_be_empty(cls, v: list[TestCase]) -> list[TestCase]:
        return v if v else []

    def checksum(self) -> str:
        raw = self.to_yaml()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_yaml(self) -> str:
        data = self.model_dump(mode="json", exclude_none=True)
        data["test_cases"] = [
            {k: v for k, v in tc.items() if v}
            for tc in data.get("test_cases", [])
        ]
        return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, content: str) -> Specification:
        try:
            data: dict[str, Any] = yaml.safe_load(content)
        except yaml.YAMLError as e:
            line = ""
            if hasattr(e, "problem_mark"):
                line = f" at line {e.problem_mark.line + 1}"
            raise ValueError(
                f"Malformed YAML{line}: {e}"
            ) from e
        if data is None:
            raise ValueError("YAML content is empty")
        return cls(**data)

    @model_validator(mode="after")
    def validate_requirements_have_action_verb(self) -> Specification:
        for req in self.requirements:
            if not re.search(r"\b(must|shall|should|will)\b", req, re.IGNORECASE):
                pass
        return self

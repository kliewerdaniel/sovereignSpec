from __future__ import annotations

from datetime import date

import pytest

from sovereignspec.models.adr import ADR, ADRStatus


class TestADRModel:
    def test_default_status(self) -> None:
        adr = ADR(number=1, title="Test")
        assert adr.status == ADRStatus.PROPOSED

    def test_default_date(self) -> None:
        adr = ADR(number=1, title="Test")
        assert adr.date == date.today().isoformat()

    def test_full_adr_creation(self) -> None:
        adr = ADR(
            number=2,
            title="Use SQLite",
            status=ADRStatus.ACCEPTED,
            date="2025-01-15",
            context="Need local storage",
            decision="Use SQLite as primary DB",
            rationale="Local-first architecture",
            alternatives="PostgreSQL, MySQL",
            consequences="No concurrent writes",
        )
        assert adr.number == 2
        assert adr.title == "Use SQLite"
        assert adr.status == ADRStatus.ACCEPTED
        assert adr.context == "Need local storage"

    def test_to_markdown(self) -> None:
        adr = ADR(
            number=3,
            title="Use JWT",
            status=ADRStatus.ACCEPTED,
            date="2025-06-01",
            context="Need stateless auth",
            decision="Use JWT tokens",
            rationale="No server-side sessions",
            alternatives="Session cookies",
            consequences="Token revocation is hard",
        )
        md = adr.to_markdown()
        assert "ADR-003: Use JWT" in md
        assert "Status: accepted" in md
        assert "Date: 2025-06-01" in md
        assert "## Context" in md
        assert "## Decision" in md
        assert "## Rationale" in md
        assert "## Alternatives Considered" in md
        assert "## Consequences" in md

    def test_from_markdown_roundtrip(self) -> None:
        original = ADR(
            number=4,
            title="Round Trip Test",
            status=ADRStatus.ACCEPTED,
            date="2025-06-15",
            context="Test context",
            decision="Test decision",
            rationale="Test rationale",
            alternatives="Alt A, Alt B",
            consequences="Consequence X",
        )
        md = original.to_markdown()
        parsed = ADR.from_markdown(md)
        assert parsed.title == original.title
        assert parsed.status == original.status
        assert parsed.date == original.date
        assert parsed.context == original.context
        assert parsed.decision == original.decision

    def test_from_markdown_partial(self) -> None:
        md = """# ADR-001: Simple ADR

Status: proposed
Date: 2025-01-01

## Context
Just a simple context

## Decision
Simple decision
"""
        adr = ADR.from_markdown(md)
        assert adr.title == "Simple ADR"
        assert adr.status == ADRStatus.PROPOSED
        assert adr.date == "2025-01-01"
        assert adr.context == "Just a simple context"

    def test_status_values(self) -> None:
        assert ADRStatus.PROPOSED.value == "proposed"
        assert ADRStatus.ACCEPTED.value == "accepted"
        assert ADRStatus.DEPRECATED.value == "deprecated"
        assert ADRStatus.SUPERSEDED.value == "superseded"

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValueError):
            ADRStatus("invalid_status")

    def test_default_empty_fields(self) -> None:
        adr = ADR(number=5, title="Minimal")
        assert adr.context == ""
        assert adr.decision == ""
        assert adr.rationale == ""
        assert adr.alternatives == ""
        assert adr.consequences == ""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ADRStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class ADR(BaseModel):
    number: int
    title: str
    status: ADRStatus = ADRStatus.PROPOSED
    date: str = Field(default_factory=lambda: date.today().isoformat())
    context: str = ""
    decision: str = ""
    rationale: str = ""
    alternatives: str = ""
    consequences: str = ""

    def to_markdown(self) -> str:
        return f"""# ADR-{self.number:03d}: {self.title}
Status: {self.status.value}
Date: {self.date}

## Context
{self.context}

## Decision
{self.decision}

## Rationale
{self.rationale}

## Alternatives Considered
{self.alternatives}

## Consequences
{self.consequences}
"""

    @classmethod
    def from_markdown(cls, content: str) -> ADR:
        lines = content.strip().split("\n")
        title_line = lines[0] if lines else ""
        title = title_line.split(":", 1)[1].strip() if ":" in title_line else ""

        status = ADRStatus.PROPOSED
        adr_date = date.today().isoformat()
        context = ""
        decision = ""
        rationale = ""
        alternatives = ""
        consequences = ""

        current_section = ""
        sections: dict[str, list[str]] = {
            "context": [],
            "decision": [],
            "rationale": [],
            "alternatives": [],
            "consequences": [],
        }

        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("Status:"):
                try:
                    status = ADRStatus(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif stripped.startswith("Date:"):
                adr_date = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("## Context"):
                current_section = "context"
            elif stripped.startswith("## Decision"):
                current_section = "decision"
            elif stripped.startswith("## Rationale"):
                current_section = "rationale"
            elif stripped.startswith("## Alternatives"):
                current_section = "alternatives"
            elif stripped.startswith("## Consequences"):
                current_section = "consequences"
            elif current_section in sections:
                sections[current_section].append(line)

        return cls(
            number=0,
            title=title,
            status=status,
            date=adr_date,
            context="\n".join(sections["context"]).strip(),
            decision="\n".join(sections["decision"]).strip(),
            rationale="\n".join(sections["rationale"]).strip(),
            alternatives="\n".join(sections["alternatives"]).strip(),
            consequences="\n".join(sections["consequences"]).strip(),
        )

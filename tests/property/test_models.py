from __future__ import annotations

from datetime import date

from hypothesis import given, strategies as st

from sovereignspec.models.adr import ADR, ADRStatus
from sovereignspec.models.task import Task, TaskStatus


_printable = st.characters(min_codepoint=32, max_codepoint=126, blacklist_categories=("Cc", "Cs", "Zs"))

adr_status_strategy = st.sampled_from(["proposed", "accepted", "deprecated", "superseded"])
task_status_strategy = st.sampled_from(["pending", "in_progress", "completed", "blocked", "failed"])


class TestADRProperty:
    @given(
        number=st.integers(min_value=1, max_value=999),
        title=st.text(alphabet=_printable, min_size=1, max_size=100).filter(lambda t: t.strip()),
        status=adr_status_strategy,
        context=st.text(alphabet=_printable, min_size=0, max_size=500),
        decision=st.text(alphabet=_printable, min_size=0, max_size=500),
    )
    def test_adr_roundtrip_via_markdown(self, number: int, title: str, status: str, context: str, decision: str) -> None:
        adr = ADR(
            number=number,
            title=title,
            status=ADRStatus(status),
            context=context,
            decision=decision,
        )
        md = adr.to_markdown()
        parsed = ADR.from_markdown(md)
        assert parsed.title == adr.title
        assert parsed.status == adr.status
        assert parsed.context == adr.context.strip()
        assert parsed.decision == adr.decision.strip()

    @given(number=st.integers(min_value=1, max_value=999))
    def test_adr_markdown_contains_number(self, number: int) -> None:
        adr = ADR(number=number, title="Test")
        md = adr.to_markdown()
        assert f"ADR-{number:03d}" in md

    @given(
        number=st.integers(min_value=0, max_value=1000),
        title=st.text(max_size=200),
    )
    def test_adr_always_has_date(self, number: int, title: str) -> None:
        adr = ADR(number=number, title=title)
        assert adr.date is not None
        assert len(adr.date) > 0

    @given(
        number=st.integers(min_value=0, max_value=1000),
        title=st.text(max_size=200),
    )
    def test_adr_default_status_proposed(self, number: int, title: str) -> None:
        adr = ADR(number=number, title=title)
        assert adr.status == ADRStatus.PROPOSED


class TestTaskProperty:
    @given(
        id=st.text(min_size=1, max_size=50),
        spec_id=st.text(min_size=1, max_size=50),
        title=st.text(min_size=1, max_size=100),
        description=st.text(max_size=500),
        status=task_status_strategy,
        parallel=st.booleans(),
    )
    def test_task_defaults_and_properties(self, id: str, spec_id: str, title: str, description: str, status: str, parallel: bool) -> None:
        task = Task(
            id=id,
            spec_id=spec_id,
            title=title,
            description=description,
            status=TaskStatus(status),
            parallel=parallel,
        )
        assert task.id == id
        assert task.spec_id == spec_id
        assert task.title == title
        assert task.description == description
        assert task.status.value == status
        assert task.parallel == parallel

    @given(
        id=st.text(min_size=1, max_size=50),
        spec_id=st.text(min_size=1, max_size=50),
        title=st.text(min_size=1, max_size=100),
    )
    def test_task_depends_on_defaults_empty(self, id: str, spec_id: str, title: str) -> None:
        task = Task(id=id, spec_id=spec_id, title=title)
        assert task.depends_on == []
        assert task.files == []

    @given(
        ids=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
        spec_id=st.text(min_size=1, max_size=50),
        title=st.text(min_size=1, max_size=100),
    )
    def test_task_depends_on_assignment(self, ids: list[str], spec_id: str, title: str) -> None:
        task = Task(id="t1", spec_id=spec_id, title=title, depends_on=ids)
        assert len(task.depends_on) == len(ids)

    @given(
        files=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
        spec_id=st.text(min_size=1, max_size=50),
        title=st.text(min_size=1, max_size=100),
    )
    def test_task_files_assignment(self, files: list[str], spec_id: str, title: str) -> None:
        task = Task(id="t1", spec_id=spec_id, title=title, files=files)
        assert len(task.files) == len(files)

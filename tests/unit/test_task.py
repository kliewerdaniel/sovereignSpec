from __future__ import annotations

import pytest

from sovereignspec.models.task import Task, TaskList, TaskStatus


class TestTaskModel:
    def test_default_status(self) -> None:
        task = Task(id="task-1", spec_id="spec-auth", title="Implement auth")
        assert task.status == TaskStatus.PENDING

    def test_default_empty_lists(self) -> None:
        task = Task(id="task-1", spec_id="spec-auth", title="Implement auth")
        assert task.depends_on == []
        assert task.files == []

    def test_default_description(self) -> None:
        task = Task(id="task-1", spec_id="spec-auth", title="Implement auth")
        assert task.description == ""

    def test_default_acceptance(self) -> None:
        task = Task(id="task-1", spec_id="spec-auth", title="Implement auth")
        assert task.acceptance == ""

    def test_parallel_flag_default(self) -> None:
        task = Task(id="task-1", spec_id="spec-auth", title="Implement auth")
        assert task.parallel is False

    def test_full_task_creation(self) -> None:
        task = Task(
            id="task-1",
            spec_id="spec-auth",
            title="Implement JWT auth",
            description="Create JWT authentication endpoints",
            status=TaskStatus.IN_PROGRESS,
            parallel=True,
            depends_on=["task-0"],
            files=["src/auth/jwt.py"],
            acceptance="POST /auth/login returns 200",
        )
        assert task.id == "task-1"
        assert task.spec_id == "spec-auth"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.parallel is True
        assert task.depends_on == ["task-0"]
        assert task.files == ["src/auth/jwt.py"]

    def test_status_values(self) -> None:
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.FAILED.value == "failed"

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValueError):
            TaskStatus("unknown")


class TestTaskListModel:
    def test_default_tasks_empty(self) -> None:
        tl = TaskList(spec_id="spec-auth")
        assert tl.tasks == []

    def test_with_tasks(self) -> None:
        tasks = [
            Task(id="t1", spec_id="spec-auth", title="Task 1"),
            Task(id="t2", spec_id="spec-auth", title="Task 2"),
        ]
        tl = TaskList(spec_id="spec-auth", tasks=tasks)
        assert len(tl.tasks) == 2

    def test_task_list_spec_id(self) -> None:
        tl = TaskList(spec_id="spec-db")
        assert tl.spec_id == "spec-db"

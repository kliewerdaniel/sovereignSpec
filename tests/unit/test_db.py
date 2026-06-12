from __future__ import annotations

from sovereignspec.persistence.db import Database


class TestDatabaseCRUD:
    def test_create_project(self, temp_db: Database) -> None:
        proj = temp_db.create_project("p1", "Test Project", "test-project")
        assert proj["name"] == "Test Project"
        assert proj["slug"] == "test-project"

    def test_get_project(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        proj = temp_db.get_project("p1")
        assert proj is not None
        assert proj["name"] == "Test"

    def test_get_project_not_found(self, temp_db: Database) -> None:
        proj = temp_db.get_project("nonexistent")
        assert proj is None

    def test_list_projects(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Project 1", "proj-1")
        temp_db.create_project("p2", "Project 2", "proj-2")
        projects = temp_db.list_projects()
        assert len(projects) == 2

    def test_create_specification(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        spec = temp_db.create_specification("s1", "p1", "spec-auth", "Auth Spec", "specs/auth.sspec", "abc123")
        assert spec["spec_id"] == "spec-auth"
        assert spec["title"] == "Auth Spec"

    def test_get_specification_by_spec_id(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-auth", "Auth", "specs/auth.sspec", "abc")
        spec = temp_db.get_specification_by_spec_id("p1", "spec-auth")
        assert spec is not None
        assert spec["title"] == "Auth"

    def test_create_relationship(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-a", "A", "a.sspec", "abc")
        temp_db.create_specification("s2", "p1", "spec-b", "B", "b.sspec", "def")
        rel = temp_db.create_relationship("r1", "s1", "s2", "DEPENDS_ON")
        assert rel["relationship_type"] == "DEPENDS_ON"

    def test_create_spec_version(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-v", "V", "v.sspec", "abc")
        ver = temp_db.create_spec_version("v1", "s1", "1.0.0", "abc123")
        assert ver["version"] == "1.0.0"

    def test_list_spec_versions(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-v", "V", "v.sspec", "abc")
        temp_db.create_spec_version("v1", "s1", "1.0.0", "abc")
        temp_db.create_spec_version("v2", "s1", "1.1.0", "def")
        versions = temp_db.list_spec_versions("s1")
        assert len(versions) == 2

    def test_create_adr(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        adr = temp_db.create_adr("a1", "p1", 1, "Use SQLite")
        assert adr["number"] == 1

    def test_create_task(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-t", "T", "t.sspec", "abc")
        task = temp_db.create_task("t1", "s1", "Implement auth")
        assert task["title"] == "Implement auth"

    def test_create_agent(self, temp_db: Database) -> None:
        agent = temp_db.create_agent("a1", "claude-code", "claude-code")
        assert agent["name"] == "claude-code"

    def test_create_artifact(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_specification("s1", "p1", "spec-t", "T", "t.sspec", "abc")
        temp_db.create_task("t1", "s1", "Task 1")
        art = temp_db.create_artifact("art1", "t1", "code", "src/auth.py")
        assert art["artifact_type"] == "code"

    def test_create_pattern(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        pat = temp_db.create_pattern("pat1", "p1", "naming", "camelCase", "function foo()")
        assert pat["name"] == "camelCase"

    def test_create_session(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        session = temp_db.create_session("sess1", "p1")
        assert session["id"] == "sess1"

    def test_end_session(self, temp_db: Database) -> None:
        temp_db.create_project("p1", "Test", "test")
        temp_db.create_session("sess1", "p1")
        temp_db.end_session("sess1")
        session = temp_db.get_session("sess1")
        assert session is not None
        assert session["ended_at"] is not None

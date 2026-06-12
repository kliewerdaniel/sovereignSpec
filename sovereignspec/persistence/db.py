from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


def _check_writable(path: Path) -> None:
    """Check that a path is writable, with an actionable error message."""
    try:
        if path.exists():
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
        else:
            path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(
            f"Cannot write to {path}. "
            f"Try: sudo chown -R $(whoami) {path.parent}  # or "
            f"chmod -R u+w {path.parent}"
        ) from None


class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        _check_writable(self.db_path.parent)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        return self.connect()

    def execute(self, sql: str, params: dict[str, Any] | tuple = (), retries: int = 3) -> sqlite3.Cursor:
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                return self.conn.execute(sql, params)
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    last_error = e
                    continue
                raise
        raise last_error  # type: ignore[misc]

    def executemany(self, sql: str, seq: list[dict[str, Any] | tuple]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, seq)

    def commit(self) -> None:
        self.conn.commit()

    # --- Migration ---

    def run_migrations(self, migrations_dir: str | Path) -> None:
        self.execute(
            "CREATE TABLE IF NOT EXISTS _migrations ("
            "  filename TEXT PRIMARY KEY,"
            "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
            ")"
        )
        migrations_path = Path(migrations_dir)
        for f in sorted(migrations_path.glob("*.sql")):
            row = self.execute(
                "SELECT filename FROM _migrations WHERE filename = ?", (f.name,)
            ).fetchone()
            if row:
                continue
            sql = f.read_text(encoding="utf-8")
            self.conn.executescript(sql)
            self.execute("INSERT INTO _migrations (filename) VALUES (?)", (f.name,))
            self.commit()

    # --- Projects CRUD ---

    def create_project(
        self, id: str, name: str, slug: str, constitution_path: str = ""
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO projects (id, name, slug, constitution_path) VALUES (?, ?, ?, ?)",
            (id, name, slug, constitution_path),
        )
        self.commit()
        return self.get_project(id)

    def get_project(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM projects WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def get_project_by_slug(self, slug: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM projects WHERE slug = ?", (slug,)).fetchone()
        return dict(row) if row else None

    def list_projects(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()]

    def update_project(self, id: str, **kwargs: Any) -> dict[str, Any] | None:
        allowed = {"name", "constitution_path", "status"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_project(id)
        updates["updated_at"] = "datetime('now')"
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        self.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            (*values, id),
        )
        self.commit()
        return self.get_project(id)

    # --- Specifications CRUD ---

    def create_specification(
        self,
        id: str,
        project_id: str,
        spec_id: str,
        title: str,
        file_path: str,
        checksum: str,
        status: str = "draft",
        version: str = "1.0.0",
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO specifications (id, project_id, spec_id, title, status, file_path, version, checksum, parent_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id, project_id, spec_id, title, status, file_path, version, checksum, parent_id),
        )
        self.commit()
        return self.get_specification(id)

    def get_specification(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM specifications WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def get_specification_by_spec_id(self, project_id: str, spec_id: str) -> dict[str, Any] | None:
        row = self.execute(
            "SELECT * FROM specifications WHERE project_id = ? AND spec_id = ?",
            (project_id, spec_id),
        ).fetchone()
        return dict(row) if row else None

    def list_specifications(self, project_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM specifications WHERE 1=1"
        params: list[Any] = []
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC"
        return [dict(r) for r in self.execute(query, params).fetchall()]

    def update_specification(self, id: str, **kwargs: Any) -> dict[str, Any] | None:
        allowed = {"title", "status", "version", "file_path", "checksum", "parent_id"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_specification(id)
        updates["updated_at"] = "datetime('now')"
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        self.execute(
            f"UPDATE specifications SET {set_clause} WHERE id = ?",
            (*values, id),
        )
        self.commit()
        return self.get_specification(id)

    # --- Spec Relationships CRUD ---

    def create_relationship(
        self,
        id: str,
        source_spec_id: str,
        target_spec_id: str,
        relationship_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO spec_relationships (id, source_spec_id, target_spec_id, relationship_type, weight, metadata_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (id, source_spec_id, target_spec_id, relationship_type, weight, json.dumps(metadata or {})),
        )
        self.commit()
        return self.get_relationship(id)

    def get_relationship(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM spec_relationships WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_relationships(self, spec_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM spec_relationships WHERE 1=1"
        params: list[Any] = []
        if spec_id:
            query += " AND (source_spec_id = ? OR target_spec_id = ?)"
            params.extend([spec_id, spec_id])
        return [dict(r) for r in self.execute(query, params).fetchall()]

    # --- Spec Versions CRUD ---

    def create_spec_version(
        self,
        id: str,
        spec_id: str,
        version: str,
        content_hash: str,
        diff_summary: str = "",
        contradictions: list[dict[str, Any]] | None = None,
        drift_score: float | None = None,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO spec_versions (id, spec_id, version, content_hash, diff_summary, contradictions_json, drift_score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id, spec_id, version, content_hash, diff_summary, json.dumps(contradictions or []), drift_score),
        )
        self.commit()
        return self.get_spec_version(id)

    def get_spec_version(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM spec_versions WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_spec_versions(self, spec_id: str) -> list[dict[str, Any]]:
        return [
            dict(r)
            for r in self.execute(
                "SELECT * FROM spec_versions WHERE spec_id = ? ORDER BY created_at DESC", (spec_id,)
            ).fetchall()
        ]

    # --- ADRs CRUD ---

    def create_adr(
        self,
        id: str,
        project_id: str,
        number: int,
        title: str,
        status: str = "proposed",
        file_path: str = "",
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO adrs (id, project_id, number, title, status, file_path) VALUES (?, ?, ?, ?, ?, ?)",
            (id, project_id, number, title, status, file_path),
        )
        self.commit()
        return self.get_adr(id)

    def get_adr(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM adrs WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_adrs(self, project_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM adrs WHERE 1=1"
        params: list[Any] = []
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        query += " ORDER BY number DESC"
        return [dict(r) for r in self.execute(query, params).fetchall()]

    def update_adr(self, id: str, **kwargs: Any) -> dict[str, Any] | None:
        allowed = {"status", "title", "file_path", "superseded_by"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_adr(id)
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        self.execute(f"UPDATE adrs SET {set_clause} WHERE id = ?", (*values, id))
        self.commit()
        return self.get_adr(id)

    # --- Tasks CRUD ---

    def create_task(
        self,
        id: str,
        spec_id: str,
        title: str,
        status: str = "pending",
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO tasks (id, spec_id, title, status, agent_id) VALUES (?, ?, ?, ?, ?)",
            (id, spec_id, title, status, agent_id),
        )
        self.commit()
        return self.get_task(id)

    def get_task(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_tasks(self, spec_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[Any] = []
        if spec_id:
            query += " AND spec_id = ?"
            params.append(spec_id)
        query += " ORDER BY created_at DESC"
        return [dict(r) for r in self.execute(query, params).fetchall()]

    def update_task(self, id: str, **kwargs: Any) -> dict[str, Any] | None:
        allowed = {"status", "agent_id", "completed_at", "output_path"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_task(id)
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        self.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", (*values, id))
        self.commit()
        return self.get_task(id)

    # --- Agents CRUD ---

    def create_agent(
        self, id: str, name: str, adapter_type: str, capabilities: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO agents (id, name, adapter_type, capabilities_json) VALUES (?, ?, ?, ?)",
            (id, name, adapter_type, json.dumps(capabilities or {})),
        )
        self.commit()
        return self.get_agent(id)

    def get_agent(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM agents WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_agents(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.execute("SELECT * FROM agents ORDER BY last_seen DESC").fetchall()]

    # --- Artifacts CRUD ---

    def create_artifact(
        self,
        id: str,
        task_id: str,
        artifact_type: str,
        file_path: str,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO artifacts (id, task_id, artifact_type, file_path) VALUES (?, ?, ?, ?)",
            (id, task_id, artifact_type, file_path),
        )
        self.commit()
        return self.get_artifact(id)

    def get_artifact(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM artifacts WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_artifacts(self, task_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM artifacts WHERE 1=1"
        params: list[Any] = []
        if task_id:
            query += " AND task_id = ?"
            params.append(task_id)
        query += " ORDER BY created_at DESC"
        return [dict(r) for r in self.execute(query, params).fetchall()]

    # --- Patterns CRUD ---

    def create_pattern(
        self,
        id: str,
        project_id: str,
        pattern_type: str,
        name: str,
        example: str,
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO patterns (id, project_id, pattern_type, name, example) VALUES (?, ?, ?, ?, ?)",
            (id, project_id, pattern_type, name, example),
        )
        self.commit()
        return self.get_pattern(id)

    def get_pattern(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM patterns WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def list_patterns(self, project_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM patterns WHERE 1=1"
        params: list[Any] = []
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        return [dict(r) for r in self.execute(query, params).fetchall()]

    # --- Sessions CRUD ---

    def create_session(
        self, id: str, project_id: str, agent_id: str | None = None, context_hash: str | None = None
    ) -> dict[str, Any]:
        self.execute(
            "INSERT INTO sessions (id, project_id, agent_id, context_hash) VALUES (?, ?, ?, ?)",
            (id, project_id, agent_id, context_hash),
        )
        self.commit()
        return self.get_session(id)

    def get_session(self, id: str) -> dict[str, Any] | None:
        row = self.execute("SELECT * FROM sessions WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def end_session(self, id: str) -> None:
        self.execute("UPDATE sessions SET ended_at = datetime('now') WHERE id = ?", (id,))
        self.commit()

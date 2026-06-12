CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    constitution_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'archived', 'frozen'))
);

CREATE TABLE IF NOT EXISTS specifications (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    spec_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','validated','approved','active','implemented','verified','archived')),
    file_path TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    checksum TEXT NOT NULL,
    parent_id TEXT REFERENCES specifications(id)
);

CREATE INDEX IF NOT EXISTS idx_specifications_project ON specifications(project_id);
CREATE INDEX IF NOT EXISTS idx_specifications_status ON specifications(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_specifications_spec_id ON specifications(project_id, spec_id);

CREATE TABLE IF NOT EXISTS spec_relationships (
    id TEXT PRIMARY KEY,
    source_spec_id TEXT NOT NULL REFERENCES specifications(id),
    target_spec_id TEXT NOT NULL REFERENCES specifications(id),
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('DEPENDS_ON','IMPLEMENTS','REFERENCES','SUPERSEDES','CONFLICTS_WITH','RELATED_TO','VALIDATES','GENERATES','REPLACES')),
    weight REAL NOT NULL DEFAULT 1.0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_relationships_source ON spec_relationships(source_spec_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON spec_relationships(target_spec_id);

CREATE TABLE IF NOT EXISTS spec_versions (
    id TEXT PRIMARY KEY,
    spec_id TEXT NOT NULL REFERENCES specifications(id),
    version TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    diff_summary TEXT NOT NULL DEFAULT '',
    contradictions_json TEXT NOT NULL DEFAULT '[]',
    drift_score REAL DEFAULT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_spec_versions ON spec_versions(spec_id, version);

CREATE TABLE IF NOT EXISTS adrs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed','accepted','deprecated','superseded')),
    file_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    superseded_by INTEGER DEFAULT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_adrs_number ON adrs(project_id, number);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    spec_id TEXT NOT NULL REFERENCES specifications(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_progress','completed','blocked','failed')),
    agent_id TEXT REFERENCES agents(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT DEFAULT NULL,
    output_path TEXT DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_spec ON tasks(spec_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    adapter_type TEXT NOT NULL CHECK(adapter_type IN ('claude-code','opencode','cursor','cline','roocode','codex','gemini-cli','aider','windsurf','continue','generic')),
    last_seen TEXT DEFAULT (datetime('now')),
    capabilities_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    artifact_type TEXT NOT NULL CHECK(artifact_type IN ('code','test','doc','config','migration','other')),
    file_path TEXT NOT NULL,
    validated INTEGER NOT NULL DEFAULT 0 CHECK(validated IN (0, 1, 2)),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_artifacts_task ON artifacts(task_id);

CREATE TABLE IF NOT EXISTS patterns (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    pattern_type TEXT NOT NULL CHECK(pattern_type IN ('naming','error-handling','testing','import','api-route','architecture','other')),
    name TEXT NOT NULL,
    example TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    agent_id TEXT REFERENCES agents(id),
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at TEXT DEFAULT NULL,
    context_hash TEXT DEFAULT NULL
);

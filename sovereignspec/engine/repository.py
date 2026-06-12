from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
}

_ENTRYPOINT_NAMES = {"main", "index", "app", "server", "cli"}


class RepositoryMapper:
    def __init__(self, root_path: str | Path):
        self.root = Path(root_path)

    def walk(self) -> list[Path]:
        files: list[Path] = []
        for p in self.root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(self.root)
                parts = rel.parts
                if any(part.startswith(".") for part in parts if part != "."):
                    continue
                if any(part == "__pycache__" or part == "node_modules" for part in parts):
                    continue
                files.append(p)
        return files

    def detect_language(self, path: Path) -> str:
        return _LANGUAGE_MAP.get(path.suffix.lower(), "unknown")

    def is_entrypoint(self, path: Path) -> bool:
        stem = path.stem.lower()
        return stem in _ENTRYPOINT_NAMES

    def is_test_file(self, path: Path) -> bool:
        stem = path.stem.lower()
        return any(stem.endswith(suffix) for suffix in [".test", ".spec", "_test", "_spec"])

    def detect_module_boundary(self, path: Path) -> bool:
        name = path.name.lower()
        return name in {"package.json", "__init__.py", "cargo.toml", "go.mod", "pyproject.toml"}

    def generate_map(self) -> dict[str, Any]:
        files = self.walk()
        language_stats: dict[str, dict[str, Any]] = {}
        entrypoints: list[dict[str, Any]] = []
        modules: dict[str, dict[str, Any]] = {}
        file_list: list[dict[str, Any]] = []

        for f in files:
            lang = self.detect_language(f)
            rel_path = str(f.relative_to(self.root))
            try:
                size = f.stat().st_size
            except OSError:
                size = 0

            file_info: dict[str, Any] = {
                "path": rel_path,
                "language": lang,
                "type": "source",
                "size_bytes": size,
            }

            if self.is_entrypoint(f):
                file_info["type"] = "entrypoint"
                entrypoints.append({"path": rel_path, "language": lang, "type": "app-entry"})

            if self.is_test_file(f):
                file_info["type"] = "test"

            file_list.append(file_info)

            if lang not in language_stats:
                language_stats[lang] = {"files": 0, "lines": 0, "size_bytes": 0}
            language_stats[lang]["files"] += 1
            language_stats[lang]["size_bytes"] += size

            parent = str(f.parent.relative_to(self.root))
            if parent not in modules:
                modules[parent] = {"files": []}
            modules[parent]["files"].append(rel_path)

        total_size = sum(s["size_bytes"] for s in language_stats.values())
        for lang in language_stats:
            language_stats[lang]["percentage"] = round(
                (language_stats[lang]["size_bytes"] / total_size * 100) if total_size > 0 else 0, 1
            )

        module_list = [
            {
                "path": path,
                "type": "module",
                "file_count": len(info["files"]),
            }
            for path, info in sorted(modules.items())
            if path != "."
        ]

        return {
            "$schema": "sovereignspec-repository-map",
            "project_name": self.root.name,
            "analyzed_at": "",
            "language_stats": language_stats,
            "entrypoints": entrypoints,
            "modules": module_list,
            "files": file_list,
        }


_RE_NAMING = re.compile(r"\b[a-z_][a-z0-9_]*\b|\b[A-Z][a-zA-Z0-9]*\b|\b[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*\b")


class PatternExtractor:
    def __init__(self, mapper: RepositoryMapper):
        self.mapper = mapper

    def extract_naming_conventions(self, files: list[Path]) -> list[dict[str, Any]]:
        camel_case = 0
        snake_case = 0
        pascal_case = 0
        total = 0

        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for match in _RE_NAMING.finditer(content):
                name = match.group()
                total += 1
                if re.match(r"^[a-z]+[A-Z][a-zA-Z0-9]*$", name):
                    camel_case += 1
                elif re.match(r"^[a-z][a-z0-9_]*$", name):
                    snake_case += 1
                elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                    pascal_case += 1

        conventions: list[dict[str, Any]] = []
        if total > 0:
            cc_pct = camel_case / total
            sc_pct = snake_case / total
            pc_pct = pascal_case / total

            if cc_pct > 0.4:
                conventions.append({
                    "type": "naming",
                    "name": "camelCase-functions",
                    "confidence": round(cc_pct, 2),
                    "description": "Functions and variables use camelCase naming",
                })
            if sc_pct > 0.4:
                conventions.append({
                    "type": "naming",
                    "name": "snake_case-variables",
                    "confidence": round(sc_pct, 2),
                    "description": "Variables use snake_case naming",
                })
            if pc_pct > 0.4:
                conventions.append({
                    "type": "naming",
                    "name": "PascalCase-classes",
                    "confidence": round(pc_pct, 2),
                    "description": "Classes use PascalCase naming",
                })

        return conventions

    def extract_patterns(self) -> dict[str, Any]:
        files = self.mapper.walk()
        naming = self.extract_naming_conventions(files)

        patterns: list[dict[str, Any]] = []
        for n in naming:
            patterns.append({
                "id": f"pattern-{n['name']}",
                "type": n["type"],
                "name": n["name"],
                "description": n["description"],
                "example": "",
                "confidence": n["confidence"],
            })

        return {
            "$schema": "sovereignspec-pattern-library",
            "patterns": patterns,
        }

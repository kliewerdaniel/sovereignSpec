from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sovereignspec.engine.repository import RepositoryMapper, PatternExtractor


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "main.py").write_text("def main():\n    pass\n")
    (tmp_path / "src" / "utils.py").write_text(
        "def get_user():\n    user_id = 1\n    user_name = 'test'\n    return User(id=user_id)\n"
    )
    (tmp_path / "src" / "test_utils.py").write_text("def test_get_user():\n    pass\n")
    (tmp_path / "src" / "utils.test.ts").write_text("")
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "README.md").write_text("# Test Repo\n")
    return tmp_path


@pytest.fixture
def mapper(sample_repo: Path) -> RepositoryMapper:
    return RepositoryMapper(sample_repo)


class TestRepositoryMapper:
    def test_walk_finds_files(self, mapper: RepositoryMapper) -> None:
        files = mapper.walk()
        paths = {str(f.relative_to(mapper.root)) for f in files}
        assert "src/main.py" in paths
        assert "src/utils.py" in paths
        assert "src/__init__.py" in paths

    def test_detect_language(self, mapper: RepositoryMapper) -> None:
        assert mapper.detect_language(Path("test.py")) == "python"
        assert mapper.detect_language(Path("test.ts")) == "typescript"
        assert mapper.detect_language(Path("test.rs")) == "rust"
        assert mapper.detect_language(Path("test.unknown")) == "unknown"

    def test_is_entrypoint(self, mapper: RepositoryMapper) -> None:
        assert mapper.is_entrypoint(Path("main.py"))
        assert mapper.is_entrypoint(Path("index.ts"))
        assert mapper.is_entrypoint(Path("app.py"))
        assert not mapper.is_entrypoint(Path("utils.py"))

    def test_is_test_file(self, mapper: RepositoryMapper) -> None:
        assert mapper.is_test_file(Path("test_utils.py"))
        assert mapper.is_test_file(Path("utils.test.ts"))
        assert mapper.is_test_file(Path("utils.spec.ts"))
        assert not mapper.is_test_file(Path("utils.py"))

    def test_detect_module_boundary(self, mapper: RepositoryMapper) -> None:
        assert mapper.detect_module_boundary(Path("package.json"))
        assert mapper.detect_module_boundary(Path("__init__.py"))
        assert mapper.detect_module_boundary(Path("Cargo.toml"))
        assert mapper.detect_module_boundary(Path("pyproject.toml"))
        assert not mapper.detect_module_boundary(Path("random.txt"))

    def test_generate_map_structure(self, mapper: RepositoryMapper) -> None:
        result = mapper.generate_map()
        assert "$schema" in result
        assert "language_stats" in result
        assert "entrypoints" in result
        assert "modules" in result
        assert "files" in result

    def test_generate_map_language_stats(self, mapper: RepositoryMapper) -> None:
        result = mapper.generate_map()
        assert "python" in result["language_stats"]

    def test_generate_map_entrypoints(self, mapper: RepositoryMapper) -> None:
        result = mapper.generate_map()
        entry_paths = [e["path"] for e in result["entrypoints"]]
        assert any("main.py" in p for p in entry_paths)


class TestPatternExtractor:
    def test_extract_naming_conventions(self, sample_repo: Path) -> None:
        mapper = RepositoryMapper(sample_repo)
        extractor = PatternExtractor(mapper)
        naming = extractor.extract_naming_conventions(mapper.walk())
        assert isinstance(naming, list)

    def test_extract_patterns_structure(self, sample_repo: Path) -> None:
        mapper = RepositoryMapper(sample_repo)
        extractor = PatternExtractor(mapper)
        patterns = extractor.extract_patterns()
        assert "$schema" in patterns
        assert "patterns" in patterns

    def test_extract_patterns_empty_repo(self, tmp_path: Path) -> None:
        mapper = RepositoryMapper(tmp_path)
        extractor = PatternExtractor(mapper)
        patterns = extractor.extract_patterns()
        assert isinstance(patterns["patterns"], list)

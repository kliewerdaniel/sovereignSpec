from __future__ import annotations

import json
from pathlib import Path

import click

from sovereignspec.cli.main import require_project_dir, verbose_option


@click.group(name="repo")
def repo() -> None:
    """Repository intelligence commands."""


@repo.command(name="map")
@click.option("--rebuild", is_flag=True, help="Force rebuild repository map")
@click.option("--project-dir", default=None)
@verbose_option
def repo_map(project_dir: str | None, verbose: bool, rebuild: bool) -> None:
    """Generate a repository map."""
    base = Path(require_project_dir(project_dir))
    from sovereignspec.engine.repository import RepositoryMapper

    mapper = RepositoryMapper(str(base))
    repo_map_data = mapper.generate_map()

    patterns_dir = base / ".sovereignspec" / "patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)

    output_path = patterns_dir / "repository_map.json"
    output_path.write_text(json.dumps(repo_map_data, indent=2))
    click.echo(f"Repository map written to {output_path}")
    click.echo(f"  Files: {len(repo_map_data['files'])}")
    click.echo(f"  Entrypoints: {len(repo_map_data['entrypoints'])}")
    click.echo(f"  Languages: {', '.join(repo_map_data['language_stats'].keys())}")


@repo.command(name="patterns")
@click.option("--project-dir", default=None)
@verbose_option
def repo_patterns(project_dir: str | None, verbose: bool) -> None:
    """Extract and display coding patterns."""
    base = Path(require_project_dir(project_dir))
    from sovereignspec.engine.repository import RepositoryMapper, PatternExtractor

    mapper = RepositoryMapper(str(base))
    extractor = PatternExtractor(mapper)
    patterns_data = extractor.extract_patterns()

    patterns_dir = base / ".sovereignspec" / "patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)

    output_path = patterns_dir / "pattern_library.json"
    output_path.write_text(json.dumps(patterns_data, indent=2))
    click.echo(f"Pattern library written to {output_path}")

    for p in patterns_data["patterns"]:
        click.echo(f"  {p['type']}: {p['name']} (confidence: {p['confidence']})")

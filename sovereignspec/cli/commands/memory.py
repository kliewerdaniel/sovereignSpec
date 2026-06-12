from __future__ import annotations

import json
from pathlib import Path

import click

from sovereignspec.cli.main import resolve_project_dir, verbose_option


@click.group(name="memory")
def memory() -> None:
    """Manage SovereignSpec memory stores."""


@memory.command(name="sync")
@click.option("--rebuild-graph", is_flag=True, help="Rebuild graph from scratch")
@click.option("--rebuild-embeddings", is_flag=True, help="Rebuild all embeddings")
@click.option("--project-dir", default=None)
@verbose_option
def memory_sync(project_dir: str | None, verbose: bool, rebuild_graph: bool, rebuild_embeddings: bool) -> None:
    """Sync memory stores (SQLite, ChromaDB, graph)."""
    base = Path(resolve_project_dir(project_dir)) / ".sovereignspec"

    click.echo("Syncing memory stores...")

    from sovereignspec.persistence import Database

    db = Database(str(base / "memory" / "sovereignspec.db"))
    db.run_migrations(str(Path(__file__).resolve().parent.parent.parent / "persistence" / "migrations"))
    click.echo("  SQLite: OK")

    try:
        from sovereignspec.persistence.chroma import ChromaStore
        chroma = ChromaStore(str(base / "memory" / "chromadb"))
        collections = chroma.list_collections()
        click.echo(f"  ChromaDB: {len(collections)} collections")
    except Exception as e:
        click.echo(f"  ChromaDB: error — {e}")

    if rebuild_graph:
        graph_data: dict[str, list] = {"nodes": [], "edges": []}
        graph_path = base / "graph" / "graph.json"
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        graph_path.write_text(json.dumps(graph_data, indent=2))
        click.echo("  Graph: rebuilt")

    click.echo("Sync complete.")


@memory.command(name="status")
@click.option("--project-dir", default=None)
def memory_status(project_dir: str | None) -> None:
    """Show memory store status."""
    base = Path(resolve_project_dir(project_dir)) / ".sovereignspec"

    try:
        from sovereignspec.persistence import Database
        db = Database(str(base / "memory" / "sovereignspec.db"))
        db.run_migrations(str(Path(__file__).resolve().parent.parent.parent / "persistence" / "migrations"))

        projects = db.list_projects()
        specs = db.list_specifications()
        adrs = db.list_adrs()
        tasks = db.list_tasks()
        agents = db.list_agents()
        patterns = db.list_patterns()
        db.close()

        click.echo("SQLite:")
        click.echo(f"  Projects: {len(projects)}")
        click.echo(f"  Specifications: {len(specs)}")
        click.echo(f"  ADRs: {len(adrs)}")
        click.echo(f"  Tasks: {len(tasks)}")
        click.echo(f"  Agents: {len(agents)}")
        click.echo(f"  Patterns: {len(patterns)}")
    except Exception as e:
        click.echo(f"  SQLite: error — {e}")

    try:
        from sovereignspec.persistence.chroma import ChromaStore
        chroma = ChromaStore(str(base / "memory" / "chromadb"))
        collections = chroma.list_collections()
        click.echo("ChromaDB:")
        for c in collections:
            click.echo(f"  {c}: {chroma.count(c)} documents")
    except Exception as e:
        click.echo(f"  ChromaDB: error — {e}")

    graph_path = base / "graph" / "graph.json"
    if graph_path.exists():
        data = json.loads(graph_path.read_text())
        click.echo(f"Knowledge Graph: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")
    else:
        click.echo("Knowledge Graph: not initialized")

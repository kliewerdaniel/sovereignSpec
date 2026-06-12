from __future__ import annotations

from pathlib import Path

import click

from sovereignspec.cli.main import resolve_project_dir, verbose_option


@click.group(name="graph")
def graph() -> None:
    """Query and manage the knowledge graph."""


@graph.command(name="query")
@click.option("--what-breaks", help="Spec ID to check impact for")
@click.option("--affects-module", help="Module path to check")
@click.option("--project-dir", default=None)
@verbose_option
def graph_query(project_dir: str | None, verbose: bool, what_breaks: str | None, affects_module: str | None) -> None:
    """Query the knowledge graph."""
    base = Path(resolve_project_dir(project_dir))
    graph_path = base / ".sovereignspec" / "graph" / "graph.json"

    if not graph_path.exists():
        click.echo("No graph.json found. Run 'sovereignspec memory sync' first.", err=True)
        return

    from sovereignspec.models.graph import KnowledgeGraph
    from sovereignspec.engine.graph import GraphEngine

    kg = KnowledgeGraph.from_json(graph_path.read_text())
    engine = GraphEngine(kg)

    if what_breaks:
        affected = engine.what_breaks_if_changed(what_breaks)
        if affected:
            click.echo(f"Changes to '{what_breaks}' will affect:")
            for node in affected:
                click.echo(f"  - {node['id']} ({node['data'].get('type', 'unknown')})")
        else:
            click.echo(f"No downstream effects found for '{what_breaks}'.")
    elif affects_module:
        specs = engine.what_specs_affect_module(affects_module)
        if specs:
            click.echo(f"Specs affecting '{affects_module}':")
            for s in specs:
                click.echo(f"  - {s}")
        else:
            click.echo(f"No specs reference '{affects_module}'.")
    else:
        click.echo("Specify --what-breaks or --affects-module.")


@graph.command(name="stats")
@click.option("--project-dir", default=None)
def graph_stats(project_dir: str | None) -> None:
    """Show graph statistics."""
    base = Path(resolve_project_dir(project_dir))
    graph_path = base / ".sovereignspec" / "graph" / "graph.json"

    if not graph_path.exists():
        click.echo("No graph.json found.", err=True)
        return

    from sovereignspec.models.graph import KnowledgeGraph
    from sovereignspec.engine.graph import GraphEngine

    kg = KnowledgeGraph.from_json(graph_path.read_text())
    engine = GraphEngine(kg)
    stats = engine.stats()

    click.echo(f"Total nodes: {stats['total_nodes']}")
    click.echo(f"Total edges: {stats['total_edges']}")
    click.echo("Node types:")
    for t, c in sorted(stats['node_types'].items()):
        click.echo(f"  {t}: {c}")
    click.echo("Edge types:")
    for t, c in sorted(stats['edge_types'].items()):
        click.echo(f"  {t}: {c}")

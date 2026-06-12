from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import click

from sovereignspec.cli.main import resolve_project_dir, verbose_option, EXIT_SUCCESS, EXIT_NO_OLLAMA


@click.command(name="doctor")
@click.option("--project-dir", default=None)
@verbose_option
def doctor(project_dir: str | None, verbose: bool) -> None:
    """Verify system health and configuration."""
    all_healthy = True

    click.echo("SovereignSpec Doctor")
    click.echo("═" * 40)

    click.echo(f"\nPython: {sys.version.split()[0]} — OK")

    base = Path(resolve_project_dir(project_dir))
    click.echo(f"\nProject directory: {base}")
    ss_path = base / ".sovereignspec"
    if ss_path.exists():
        click.echo("  Project initialized: Yes")
    else:
        click.echo("  Project initialized: No (run 'sovereignspec init')")
        all_healthy = False

    click.echo("\nOllama:")
    from sovereignspec.engine.grammar import OllamaClient
    llm = OllamaClient()
    if llm.health():
        click.echo("  Connectivity: OK")
    else:
        click.echo("  Connectivity: FAILED — Is Ollama running on localhost:11434?")
        all_healthy = False

    click.echo("\nSQLite:")
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("SELECT 1")
        conn.close()
        click.echo("  Availability: OK")
    except Exception as e:
        click.echo(f"  Availability: FAILED — {e}")
        all_healthy = False

    click.echo("\nChromaDB:")
    try:
        import chromadb
        client = chromadb.PersistentClient(
            path=str(ss_path / "memory" / "chromadb"),
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        client.heartbeat()
        click.echo("  Availability: OK")
    except Exception as e:
        click.echo(f"  Availability: FAILED — {e}")
        all_healthy = False

    click.echo(f"\nFilesystem:")
    memory_path = ss_path / "memory"
    if memory_path.exists():
        click.echo(f"  Memory path: {memory_path} — OK")
    else:
        click.echo(f"  Memory path: {memory_path} — will be created on first use")

    if all_healthy:
        click.echo("\n✓ All checks passed.")
        sys.exit(EXIT_SUCCESS)
    else:
        click.echo("\n✗ Some checks failed. See messages above.")
        sys.exit(EXIT_NO_OLLAMA)

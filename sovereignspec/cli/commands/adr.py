from __future__ import annotations

from pathlib import Path

import click

from sovereignspec.cli.main import require_project_dir


@click.group(name="adr")
def adr() -> None:
    """Manage Architecture Decision Records."""


@adr.command(name="create")
@click.option("--title", prompt=True, help="ADR title")
@click.option("--context", prompt=True, help="Decision context")
@click.option("--project-dir", default=None)
def adr_create(project_dir: str | None, title: str, context: str) -> None:
    """Create a new Architecture Decision Record."""
    base = Path(require_project_dir(project_dir))
    adr_dir = base / ".sovereignspec" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    existing = list(adr_dir.glob("ADR-*.md"))
    next_num = max((int(f.stem.split("-")[1]) for f in existing), default=0) + 1

    from sovereignspec.models.adr import ADR

    record = ADR(
        number=next_num,
        title=title,
        context=context,
    )
    file_path = adr_dir / f"ADR-{next_num:03d}.md"
    file_path.write_text(record.to_markdown())
    click.echo(f"Created {file_path}")


@adr.command(name="update")
@click.argument("number", type=int)
@click.option("--status", type=click.Choice(["proposed", "accepted", "deprecated", "superseded"]), help="New status")
@click.option("--superseded-by", type=int, help="ADR number that supersedes this one")
@click.option("--project-dir", default=None)
def adr_update(
    project_dir: str | None,
    number: int,
    status: str | None,
    superseded_by: int | None,
) -> None:
    """Update an ADR's status."""
    base = Path(require_project_dir(project_dir))
    adr_dir = base / ".sovereignspec" / "adr"
    file_path = adr_dir / f"ADR-{number:03d}.md"
    if not file_path.exists():
        click.echo(f"ADR-{number:03d} not found")
        raise SystemExit(1)

    from sovereignspec.models.adr import ADR

    record = ADR.from_markdown(file_path.read_text())
    if status:
        from sovereignspec.models.adr import ADRStatus
        record.status = ADRStatus(status)
    file_path.write_text(record.to_markdown())
    click.echo(f"Updated ADR-{number:03d} to status={record.status.value}")


@adr.command(name="list")
@click.option("--project-dir", default=None)
def adr_list(project_dir: str | None) -> None:
    """List all ADRs."""
    base = Path(require_project_dir(project_dir))
    adr_dir = base / ".sovereignspec" / "adr"
    if not adr_dir.exists():
        click.echo("No ADRs found.")
        return

    paths = sorted(adr_dir.glob("ADR-*.md"))
    if not paths:
        click.echo("No ADRs found.")
        return

    from sovereignspec.models.adr import ADR

    for p in paths:
        try:
            record = ADR.from_markdown(p.read_text())
            num = int(p.stem.split("-")[1]) if "-" in p.stem else record.number
            click.echo(f"ADR-{num:03d}  [{record.status.value}]  {record.title}")
        except Exception:
            click.echo(f"{p.stem}  (parse error)")

from __future__ import annotations

from pathlib import Path

import click

from sovereignspec.cli.main import resolve_project_dir, verbose_option
from sovereignspec.models.spec import Specification


@click.group(name="spec")
def spec() -> None:
    """Manage specifications."""


@spec.command(name="create")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
def spec_create(spec_id: str, project_dir: str | None) -> None:
    """Create a new .sspec specification file."""
    base = Path(resolve_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    file_path = specs_dir / f"{spec_id}.sspec"

    if file_path.exists():
        click.echo(f"Error: {file_path} already exists.", err=True)
        raise click.Abort()

    spec = Specification(
        id=spec_id,
        title=spec_id.replace("-", " ").title(),
        version="1.0.0",
        status="draft",
    )
    file_path.write_text(spec.to_yaml())
    click.echo(f"Created {file_path}")


@spec.command(name="validate")
@click.argument("spec_id", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Validate all specs")
@click.option("--project-dir", default=None)
@verbose_option
def spec_validate(spec_id: str | None, project_dir: str | None, verbose: bool, all_flag: bool) -> None:
    """Validate a specification against all rules."""
    base = Path(resolve_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"

    if all_flag:
        spec_paths = sorted(specs_dir.glob("*.sspec"))
    elif spec_id:
        spec_paths = [specs_dir / f"{spec_id}.sspec"]
    else:
        click.echo("Specify a spec-id or use --all", err=True)
        raise click.Abort()

    from sovereignspec.engine.validator import ValidationContext, create_default_validator

    validator = create_default_validator()

    for spec_path in spec_paths:
        if not spec_path.exists():
            click.echo(f"Error: {spec_path} not found.", err=True)
            continue

        spec = Specification.from_yaml(spec_path.read_text())
        vctx = ValidationContext()
        errors = validator.validate(spec, vctx)

        if errors:
            click.echo(f"\n{spec.id} ({len(errors)} errors):")
            for e in errors:
                click.echo(f"  [{e.code}] {e.message}")
        else:
            click.echo(f"{spec.id}: All validation rules passed.")


@spec.command(name="compile")
@click.argument("spec_id", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Compile all specs")
@click.option("--project-dir", default=None)
@verbose_option
def spec_compile(spec_id: str | None, project_dir: str | None, verbose: bool, all_flag: bool) -> None:
    """Run the compiler pipeline on a specification."""
    base = Path(resolve_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"
    from sovereignspec.engine.compiler import Compiler

    if all_flag:
        spec_paths = sorted(specs_dir.glob("*.sspec"))
    elif spec_id:
        spec_paths = [specs_dir / f"{spec_id}.sspec"]
    else:
        click.echo("Specify a spec-id or use --all", err=True)
        raise click.Abort()

    compiler = Compiler()

    for spec_path in spec_paths:
        if not spec_path.exists():
            click.echo(f"Error: {spec_path} not found.", err=True)
            continue

        spec = Specification.from_yaml(spec_path.read_text())
        result = compiler.compile_spec(spec)

        if result.success:
            click.echo(f"{spec.id}: Compiled successfully ({len(result.steps_completed)} steps)")
        else:
            click.echo(f"{spec.id}: Compilation failed — {result.errors}")


@spec.command(name="list")
@click.option("--status", help="Filter by status (draft, active, etc.)")
@click.option("--project-dir", default=None)
def spec_list(project_dir: str | None, status: str | None) -> None:
    """List all specifications."""
    base = Path(resolve_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"
    spec_paths = sorted(specs_dir.glob("*.sspec"))

    if not spec_paths:
        click.echo("No specifications found.")
        return

    for spec_path in spec_paths:
        try:
            spec = Specification.from_yaml(spec_path.read_text())
            if status and spec.status.value != status:
                continue
            click.echo(f"{spec.id:<30} v{spec.version:<8} {spec.status.value:<12} {spec.title}")
        except Exception:
            click.echo(f"{spec_path.name:<30} (parse error)")


@spec.command(name="diff")
@click.argument("spec_id")
@click.option("--v1", "version_a", help="First version")
@click.option("--v2", "version_b", help="Second version")
@click.option("--project-dir", default=None)
def spec_diff(spec_id: str, project_dir: str | None, version_a: str | None, version_b: str | None) -> None:
    """Show semantic diff between spec versions."""
    click.echo(f"Diff for {spec_id} (versions {version_a or 'current'} vs {version_b or 'previous'}): Not yet implemented")


@spec.command(name="graph")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
def spec_graph(spec_id: str, project_dir: str | None) -> None:
    """Visualize a spec's position in the knowledge graph."""
    click.echo(f"Graph visualization for {spec_id}: Not yet implemented")

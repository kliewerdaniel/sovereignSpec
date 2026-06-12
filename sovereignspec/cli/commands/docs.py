from __future__ import annotations

from pathlib import Path

import click

from sovereignspec.cli.main import require_project_dir, verbose_option


@click.command(name="docs")
@click.argument("spec_id", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Generate docs for all specs")
@click.option("--format", "output_format", default="markdown", help="Output format (markdown|html)")
@click.option("--project-dir", default=None)
@verbose_option
def docs(spec_id: str | None, project_dir: str | None, verbose: bool, all_flag: bool, output_format: str) -> None:
    """Generate documentation bundle for a specification."""
    base = Path(require_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"
    docs_dir = base / ".sovereignspec" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    from sovereignspec.models.spec import Specification

    if all_flag:
        spec_paths = sorted(specs_dir.glob("*.sspec"))
    elif spec_id:
        spec_paths = [specs_dir / f"{spec_id}.sspec"]
    else:
        click.echo("Specify a spec-id or use --all", err=True)
        raise click.Abort()

    for spec_path in spec_paths:
        if not spec_path.exists():
            click.echo(f"Error: {spec_path} not found.", err=True)
            continue

        spec = Specification.from_yaml(spec_path.read_text())
        spec_docs_dir = docs_dir / spec.id
        spec_docs_dir.mkdir(parents=True, exist_ok=True)

        doc_content = f"""# {spec.title}

**ID:** {spec.id}
**Version:** {spec.version}
**Status:** {spec.status.value}

## Purpose
{spec.purpose}

## Requirements
"""
        for req in spec.requirements:
            doc_content += f"- {req}\n"

        doc_content += "\n## Constraints\n"
        for c in spec.constraints:
            doc_content += f"- {c}\n"

        doc_content += "\n## Acceptance Criteria\n"
        for ac in spec.acceptance_criteria:
            doc_content += f"- {ac}\n"

        doc_content += "\n## Dependencies\n"
        for dep in spec.dependencies:
            doc_content += f"- {dep}\n"
        if not spec.dependencies:
            doc_content += "- None\n"

        ext = ".html" if output_format == "html" else ".md"
        output_path = spec_docs_dir / f"specification{ext}"
        output_path.write_text(doc_content)

        click.echo(f"Generated {output_path}")

from __future__ import annotations

from pathlib import Path

import click

from sovereignspec.cli.main import model_option, require_project_dir


@click.command(name="context")
@click.argument("spec_id")
@click.option("--agent", default="generic", help="Target agent adapter name")
@click.option("--project-dir", default=None)
@model_option
def context(spec_id: str, project_dir: str | None, model: str | None, agent: str) -> None:
    """Assemble an agent context package for a specification."""
    base = Path(require_project_dir(project_dir))
    specs_dir = base / ".sovereignspec" / "specs"
    spec_path = specs_dir / f"{spec_id}.sspec"

    if not spec_path.exists():
        click.echo(f"Error: spec '{spec_id}' not found.", err=True)
        raise click.Abort()

    from sovereignspec.models.spec import Specification
    spec = Specification.from_yaml(spec_path.read_text())

    context_path = base / ".sovereignspec" / "agents" / agent
    context_path.mkdir(parents=True, exist_ok=True)

    from sovereignspec.engine.grammar import OllamaClient
    from sovereignspec.engine.rag import RAGPipeline
    from sovereignspec.persistence.chroma import ChromaStore

    llm = OllamaClient()
    chroma = ChromaStore(str(base / ".sovereignspec" / "memory" / "chromadb"))
    rag = RAGPipeline(chroma, llm)

    context_content = rag.build_context(spec_id, spec.to_yaml())

    output_path = context_path / f"{spec_id}_context.md"
    output_path.write_text(context_content)
    click.echo(f"Context package written to {output_path}")

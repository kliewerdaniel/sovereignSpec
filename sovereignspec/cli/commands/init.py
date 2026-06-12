from __future__ import annotations

import json
import shutil
from pathlib import Path

import click


@click.command(name="init")
@click.argument("path", default=".", type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.option("--force", is_flag=True, help="Overwrite existing files")
@click.option("--model", default="qwen2.5-coder:7b", help="Default Ollama model (smaller)")
@click.option("--adapter", default="generic", help="Agent adapter to configure")
def init(path: str, force: bool, model: str, adapter: str) -> None:
    """Initialize a new SovereignSpec project at PATH."""
    project_dir = Path(path)
    project_dir.mkdir(parents=True, exist_ok=True)
    ss_dir = project_dir / ".sovereignspec"

    if ss_dir.exists() and not force:
        click.echo(f"Error: {ss_dir} already exists. Use --force to overwrite.", err=True)
        raise click.Abort()

    # Ensure watch_dirs exist
    (ss_dir / "specs").mkdir(parents=True, exist_ok=True)
    (ss_dir / "adr").mkdir(parents=True, exist_ok=True)
    for d in dirs:
        (ss_dir / d).mkdir(parents=True, exist_ok=True)

    bootstrap_src = Path(__file__).resolve().parent.parent.parent.parent / ".sovereignspec" / "bootstrap.md"
    if bootstrap_src.exists():
        shutil.copy2(bootstrap_src, ss_dir / "bootstrap.md")

    templates_src = Path(__file__).resolve().parent.parent.parent.parent / ".sovereignspec" / "templates"
    if templates_src.exists():
        for t in templates_src.iterdir():
            if t.is_file():
                shutil.copy2(t, ss_dir / "templates" / t.name)

    config = {
        "sovereignspec_version": "1.0.0",
        "models": {
            "generation": model,
            "embeddings": "nomic-embed-text",
            "analysis": "llama3.1:8b",
        },
        "ollama": {
            "host": "http://localhost:11434",
            "timeout": 120,
            "stream": False,
        },
        "adapter": adapter,
        "watcher": {
            "enabled": True,
            "debounce_ms": 500,
            "watch_dirs": ["specs", "adr", "constitution.md"],
        },
    }

    # Write sovereignspec.yaml with correct llm config
    import yaml
    ss_yaml = {
        "llm": {
            "provider": "ollama",
            "host": "http://localhost:11434",
            "timeout": 120,
            "models": [
                {"name": model, "role": "generation"},
                {"name": "nomic-embed-text", "role": "embeddings"},
                {"name": "llama3.1:8b", "role": "analysis"},
            ],
        },
        "adapter": adapter,
    }
    (ss_dir / "sovereignspec.yaml").write_text(yaml.safe_dump(ss_yaml, sort_keys=False))

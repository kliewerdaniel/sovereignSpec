from __future__ import annotations

import click

from sovereignspec.cli.main import model_option, require_project_dir
from sovereignspec.engine.grammar import OllamaClient


@click.command(name="sovereign-constitution")
@click.argument("description", required=False)
@click.option("--project-dir", default=None)
@model_option
def sovereign_constitution(description: str | None, project_dir: str | None, model: str | None) -> None:
    """Generate or update the project constitution from a description."""
    base = require_project_dir(project_dir)
    if description:
        click.echo(f"Generating constitution for: {description}")
        client = OllamaClient()
        resp = client.generate(prompt=description, model=model or "qwen2.5-coder:32b")
        click.echo(resp.get("response", ""))
    else:
        click.echo("Usage: sovereignspec sovereign-constitution <description>")


@click.command(name="specify")
@click.argument("description", nargs=-1)
@click.option("--project-dir", default=None)
@model_option
def specify(description: tuple[str, ...], project_dir: str | None, model: str | None) -> None:
    """Define a new feature spec from a description."""
    desc = " ".join(description)
    if desc:
        click.echo(f"Creating spec from: {desc}")
        click.echo("  (LLM generation not yet connected — placeholder)")
    else:
        click.echo("Usage: sovereignspec specify <feature description>")


@click.command(name="clarify")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
@model_option
def clarify(spec_id: str, project_dir: str | None, model: str | None, question: str | None) -> None:
    """RAG-grounded clarification of a spec."""
    client = OllamaClient()
    prompt = f"Provide clarification for spec {spec_id}: {question or ''}"
    resp = client.generate(prompt=prompt, model=model or "qwen2.5-coder:32b")
    click.echo(resp.get("response", ""))


@click.command(name="plan")
@click.argument("spec_id")
@click.option("--tech-stack", help="Technology stack hints")
@click.option("--project-dir", default=None)
@model_option
def plan(spec_id: str, project_dir: str | None, model: str | None, tech_stack: str | None) -> None:
    """Generate technical implementation plan for a spec."""
    client = OllamaClient()
    prompt = f"Generate implementation plan for spec {spec_id}."
    if tech_stack:
        prompt += f" Use tech stack: {tech_stack}."
    resp = client.generate(prompt=prompt, model=model or "qwen2.5-coder:32b")
    click.echo(resp.get("response", ""))


@click.command(name="tasks")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
@model_option
@click.command(name="tasks")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
@model_option
def tasks_cmd(spec_id: str, project_dir: str | None, model: str | None) -> None:
    """Generate task decomposition for a spec."""
    client = OllamaClient()
    prompt = f"Generate task decomposition for spec {spec_id}."
    resp = client.generate(prompt=prompt, model=model or "qwen2.5-coder:32b")
    click.echo(resp.get("response", ""))


@click.command(name="analyze")
@click.argument("spec_id", required=False)
@click.option("--all", "all_flag", is_flag=True, help="Analyze all specs")
@click.option("--project-dir", default=None)
def analyze(spec_id: str | None, project_dir: str | None, all_flag: bool) -> None:
    """Cross-spec contradiction and drift analysis."""
    target = "--all" if all_flag else spec_id
    click.echo(f"Analyzing {target}...")
    client = OllamaClient()
    prompt = f"Analyze {'all specs' if all_flag else f'spec {spec_id}'} for contradictions and drift."
    resp = client.generate(prompt=prompt, model=model or "qwen2.5-coder:32b")
    click.echo(resp.get("response", ""))


@click.command(name="implement")
@click.argument("spec_id")
@click.option("--project-dir", default=None)
@model_option
def implement(spec_id: str, project_dir: str | None, model: str | None) -> None:
    """Execute implementation against spec constraints."""
    click.echo(f"Building agent context package for {spec_id}...")
    client = OllamaClient()
    prompt = f"Implement spec {spec_id} based on constraints."
    resp = client.generate(prompt=prompt, model=model or "qwen2.5-coder:32b")
    click.echo(resp.get("response", ""))

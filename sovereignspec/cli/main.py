from __future__ import annotations

import os
import sys

import click

from sovereignspec import __version__

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_NO_OLLAMA = 3
EXIT_NO_PROJECT = 4
EXIT_VALIDATION_FAILED = 5


def resolve_project_dir(project_dir: str | None = None) -> str:
    return project_dir or os.environ.get("SOVEREIGNSPEC_PROJECT_DIR", os.getcwd())


def project_dir_option(f: click.decorators.FC) -> click.decorators.FC:
    return click.option(
        "--project-dir",
        default=None,
        help="Project directory path",
        type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    )(f)


def model_option(f: click.decorators.FC) -> click.decorators.FC:
    return click.option("--model", default=None, help="Ollama model name")(f)


def verbose_option(f: click.decorators.FC) -> click.decorators.FC:
    return click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose output")(f)


def json_option(f: click.decorators.FC) -> click.decorators.FC:
    return click.option("--json", is_flag=True, default=False, help="Output in JSON format")(f)


_COMMANDS: dict[str, str] = {
    "init": "init.init",
    "doctor": "doctor.doctor",
    "spec": "spec.spec",
    "sovereign-constitution": "sovereign.sovereign_constitution",
    "specify": "sovereign.specify",
    "clarify": "sovereign.clarify",
    "plan": "sovereign.plan",
    "tasks": "sovereign.tasks_cmd",
    "analyze": "sovereign.analyze",
    "implement": "sovereign.implement",
    "graph": "graph.graph",
    "context": "context.context",
    "adr": "adr.adr",
    "memory": "memory.memory",
    "repo": "repo.repo",
    "docs": "docs.docs",
}


class SovereignSpecCLI(click.MultiCommand):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(_COMMANDS)

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        if name not in _COMMANDS:
            return None
        mod_path, attr = _COMMANDS[name].split(".")
        try:
            mod = __import__(f"sovereignspec.cli.commands.{mod_path}", fromlist=[""])
            return getattr(mod, attr)
        except (ImportError, AttributeError):
            return None


@click.command(
    cls=SovereignSpecCLI,
    invoke_without_command=True,
    help="Local-first, fully offline Spec-Driven Development engine.",
)
@click.version_option(version=__version__, prog_name="sovereignspec")
@click.pass_context
def cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(f"SovereignSpec v{__version__}")
        click.echo("Use 'sovereignspec --help' for available commands.")
        sys.exit(EXIT_SUCCESS)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()

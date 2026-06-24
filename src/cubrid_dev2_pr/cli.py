"""Command-line interface (Typer).

A single-command app: running ``cubrid-dev2-pr`` lists open teammate PRs;
``--tui`` launches the interactive Textual UI.
"""

from __future__ import annotations

import typer
from rich.console import Console

from cubrid_dev2_pr import __version__
from cubrid_dev2_pr.config import DEFAULT_LIMIT, DEFAULT_REPO, DEFAULT_REVIEWER

app = typer.Typer(
    add_completion=False,
    help="Track open CUBRID dev2 teammate PRs with review and approval state.",
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"cubrid-dev2-pr {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    repo: str = typer.Option(DEFAULT_REPO, "--repo", help="Target OWNER/REPO."),
    reviewer: str = typer.Option(
        DEFAULT_REVIEWER, "--reviewer", help="Login whose review state is shown."
    ),
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help="Max PRs to fetch."),
    drafts: bool = typer.Option(False, "--drafts", "--include-drafts", help="Include draft PRs."),
    tui: bool = typer.Option(False, "--tui", help="Launch the interactive TUI."),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """List open PRs from configured teammates (default), or launch the TUI."""
    # Milestone 2-8: load config, fetch via gh, then render the table or run the TUI.
    console.print("[yellow]cubrid-dev2-pr scaffold[/] — not yet implemented.")
    console.print(
        f"Resolved options: repo={repo!r} reviewer={reviewer!r} "
        f"limit={limit} drafts={drafts} tui={tui}"
    )
    raise typer.Exit()


def run() -> None:
    """Console-script entry point."""
    app()

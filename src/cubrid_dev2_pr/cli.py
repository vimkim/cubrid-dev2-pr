"""Command-line interface (Typer).

A single-command app: running ``cubrid-dev2-pr`` lists open teammate PRs;
``--tui`` launches the interactive Textual UI. CLI flags override config-file
values (a ``None`` default marks a flag as "not passed").
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.text import Text

from cubrid_dev2_pr import __version__, config, gh, render

app = typer.Typer(
    add_completion=False,
    help="Track open CUBRID dev2 teammate PRs with review and approval state.",
)


def _version_callback(value: bool) -> None:
    if value:
        Console().print(f"cubrid-dev2-pr {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    repo: str | None = typer.Option(None, "--repo", help="Target OWNER/REPO. Overrides config."),
    reviewer: str | None = typer.Option(
        None, "--reviewer", help="Login whose review state is shown. Overrides config."
    ),
    limit: int | None = typer.Option(None, "--limit", help="Max PRs to fetch. Overrides config."),
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
    out = Console()
    err = Console(stderr=True)

    try:
        cfg = config.load_config()
        repo_v = repo if repo is not None else cfg.repo
        reviewer_v = reviewer if reviewer is not None else cfg.reviewer
        limit_v = limit if limit is not None else cfg.limit
        gh.ensure_gh_available()
        prs = gh.fetch_pr_list(repo_v, limit_v)
    except (config.ConfigError, gh.GhError) as exc:
        err.print(Text(f"error: {exc}", style="red"))
        raise typer.Exit(code=1) from exc

    teammates = set(cfg.teammates)
    prs = [pr for pr in prs if pr.author_login in teammates]
    if not drafts:
        prs = [pr for pr in prs if not pr.is_draft]
    prs.sort(key=lambda pr: pr.created_at, reverse=True)

    if tui:
        err.print(Text("TUI mode is not implemented yet (Milestone 7).", style="yellow"))
        raise typer.Exit(code=1)

    header = f"Open PRs in {repo_v} from configured teammates — reviewer: {reviewer_v}"
    if not drafts:
        header += "  (drafts hidden; use --drafts)"
    out.print(header)
    render.render(prs, reviewer_v, console=out)


def run() -> None:
    """Console-script entry point."""
    app()

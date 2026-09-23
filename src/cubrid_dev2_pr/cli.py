"""Command-line interface (Typer).

A single-command app: running ``cubrid-dev2-pr`` lists open teammate PRs;
``--tui`` launches the interactive Textual UI. CLI flags override config-file
values (a ``None`` default marks a flag as "not passed").
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import typer
from rich.console import Console
from rich.text import Text

from cubrid_dev2_pr import __version__, config, gh, render, review
from cubrid_dev2_pr.models import PullRequest

app = typer.Typer(
    add_completion=False,
    help="Track open CUBRID dev2 teammate PRs with review and approval state.",
)


def _version_callback(value: bool) -> None:
    if value:
        Console().print(f"cubrid-dev2-pr {__version__}")
        raise typer.Exit()


def _json_record(pr: PullRequest, reviewer: str) -> dict[str, Any]:
    """Build one stable machine-readable row from the displayed PR model."""
    approved, pool = review.approval_stats(pr)
    return {
        "number": pr.number,
        "title": pr.title,
        "url": pr.url,
        "author_login": pr.author_login,
        "created_at": pr.created_at,
        "is_draft": pr.is_draft,
        "approved_count": approved,
        "reviewer_pool_count": pool,
        "requested": review.is_requested_to(pr, reviewer),
        "review_state": review.review_label(pr, reviewer),
    }


@app.callback(invoke_without_command=True)
def main(
    repo: str | None = typer.Option(None, "--repo", help="Target OWNER/REPO. Overrides config."),
    reviewer: str | None = typer.Option(
        None, "--reviewer", help="Login whose review state is shown. Overrides config."
    ),
    limit: int | None = typer.Option(None, "--limit", help="Max PRs to fetch. Overrides config."),
    since_months: int | None = typer.Option(
        None,
        "--since-months",
        help="Only PRs created within the last N months (0 = no bound). Overrides config.",
    ),
    drafts: bool = typer.Option(False, "--drafts", "--include-drafts", help="Include draft PRs."),
    tui: bool = typer.Option(False, "--tui", help="Launch the interactive TUI."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
    requested_only: bool = typer.Option(
        False,
        "--requested-only",
        help="Only include PRs directly requesting review from the configured reviewer.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """List open PRs from configured teammates (default), or launch the TUI."""
    if json_output and tui:
        raise typer.BadParameter("--json cannot be combined with --tui")

    out = Console()
    err = Console(stderr=True)

    try:
        cfg = config.load_config()
        repo_v = repo if repo is not None else cfg.repo
        reviewer_v = reviewer if reviewer is not None else cfg.reviewer
        limit_v = limit if limit is not None else cfg.limit
        since_months_v = since_months if since_months is not None else cfg.since_months
        cutoff = gh.months_ago(date.today(), since_months_v)
        created_since = cutoff.isoformat() if cutoff else None
        gh.ensure_gh_available()
        prs = gh.fetch_pr_list(repo_v, limit_v, created_since)
    except (config.ConfigError, gh.GhError) as exc:
        err.print(Text(f"error: {exc}", style="red"))
        raise typer.Exit(code=1) from exc

    teammates = set(cfg.teammates)
    prs = [pr for pr in prs if pr.author_login in teammates]
    if not drafts:
        prs = [pr for pr in prs if not pr.is_draft]
    prs.sort(key=lambda pr: pr.created_at, reverse=True)
    if requested_only:
        prs = [pr for pr in prs if review.is_requested_to(pr, reviewer_v)]

    if json_output:
        typer.echo(
            json.dumps(
                [_json_record(pr, reviewer_v) for pr in prs],
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if requested_only and not prs:
        out.print(f"No open PRs directly request review from {reviewer_v}.")
        return

    if tui:
        from cubrid_dev2_pr.tui.app import run_tui

        run_tui(prs, repo_v, reviewer_v)
        return

    header = f"Open PRs in {repo_v} from configured teammates — reviewer: {reviewer_v}"
    if created_since is not None:
        header += f"  (since {created_since})"
    if not drafts:
        header += "  (drafts hidden; use --drafts)"
    if requested_only:
        header += "  (requested only)"
    out.print(header)
    render.render(prs, reviewer_v, console=out)


def run() -> None:
    """Console-script entry point."""
    app()

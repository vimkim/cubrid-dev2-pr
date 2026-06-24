"""Rich rendering of the default (non-TUI) colored table.

Color is auto-disabled by Rich when stdout is not a TTY or ``NO_COLOR`` is set.
User-derived strings (title, author, url) are wrapped in ``Text`` so bracketed
content like ``[CBRD-12345]`` is never mistaken for console markup.
"""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from cubrid_dev2_pr import review
from cubrid_dev2_pr.models import PullRequest

_REVIEW_STYLES = {
    review.APPROVED: "green",
    review.CHANGES_REQUESTED: "red",
    review.COMMENTED_ONLY: "dim",
    review.NOT_REVIEWED: "yellow",
    review.SELF_AUTHORED: "cyan",
}


def ratio_style(approved: int, pool: int) -> str:
    """Pick a color for the approval ratio cell."""
    if pool == 0:
        return "dim"
    if approved == 0:
        return "red"
    if approved < pool:
        return "yellow"
    return "green"


def review_style(label: str) -> str:
    """Pick a color for a my-review label."""
    return _REVIEW_STYLES.get(label, "")


def build_table(prs: list[PullRequest], reviewer: str) -> Table:
    """Build the colored Rich table for the given PRs."""
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold", expand=False)
    table.add_column("PR", justify="right", no_wrap=True)
    table.add_column("AUTHOR", no_wrap=True)
    table.add_column("OPENED", no_wrap=True)
    table.add_column("APPROVALS", justify="right", no_wrap=True)
    table.add_column("MY REVIEW", no_wrap=True)
    # The URL rides on a dim second line under the title (like the prototype),
    # so the fixed columns above are never squeezed by a greedy URL column.
    table.add_column("TITLE", overflow="fold")

    for pr in prs:
        approved, pool = review.approval_stats(pr)
        label = review.review_label(pr, reviewer)
        title = ("[DRAFT] " if pr.is_draft else "") + pr.title
        title_cell = Text(title)
        title_cell.append("\n")
        title_cell.append(pr.url, style="dim")
        table.add_row(
            Text(f"#{pr.number}", style="bold"),
            Text(pr.author_login),
            Text(pr.created_at[:10]),
            Text(f"{approved}/{pool}", style=ratio_style(approved, pool)),
            Text(label, style=review_style(label)),
            title_cell,
        )
    return table


def render(prs: list[PullRequest], reviewer: str, console: Console | None = None) -> None:
    """Print the table (or an empty-state message) to the console."""
    console = console or Console()
    if not prs:
        console.print("No open PRs from configured teammates.")
        return
    console.print(build_table(prs, reviewer))

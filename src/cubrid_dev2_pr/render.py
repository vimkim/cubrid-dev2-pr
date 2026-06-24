"""Rich rendering of the default (non-TUI) colored table.

Color is auto-disabled by Rich when stdout is not a TTY or ``NO_COLOR`` is set.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from cubrid_dev2_pr.models import PullRequest


def build_table(prs: list[PullRequest], reviewer: str) -> Table:
    """Build the colored Rich table for the given PRs.

    Milestone 5: columns (PR, author, opened, approvals, my review, title, url)
    with conditional coloring of approval ratio and review state.
    """
    raise NotImplementedError("Milestone 5: build Rich table")


def render(prs: list[PullRequest], reviewer: str, console: Console | None = None) -> None:
    """Print the table to the console.

    Milestone 5: instantiate a :class:`~rich.console.Console` when not given and
    print :func:`build_table`.
    """
    raise NotImplementedError("Milestone 5: render table")

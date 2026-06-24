"""Textual detail screen for a single PR.

M7 shows the PR metadata. M8 adds the lazily-fetched, cached, markdown-rendered
body and the reviewer-status list. Esc returns to the list; ``q`` quits.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Static

from cubrid_dev2_pr import render, review
from cubrid_dev2_pr.models import PullRequest


def _line(label: str, value: Text) -> Static:
    """A bold fixed-width label followed by a (possibly styled) value."""
    return Static(Text.assemble((f"{label:<11}", "bold"), value))


class DetailScreen(Screen[None]):
    """Read-only detail view for one pull request."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(self, pr: PullRequest, repo: str, reviewer: str) -> None:
        super().__init__()
        self._pr = pr
        self._repo = repo
        self._reviewer = reviewer

    def compose(self) -> ComposeResult:
        pr = self._pr
        approved, pool = review.approval_stats(pr)
        label = review.review_label(pr, self._reviewer)
        with VerticalScroll():
            yield Static(Text(f"#{pr.number}  {pr.title}", style="bold"))
            yield Static("")
            yield _line("Author", Text(pr.author_login))
            yield _line("Opened", Text(pr.created_at[:10]))
            yield _line(
                "Approvals",
                Text(f"{approved}/{pool}", style=render.ratio_style(approved, pool)),
            )
            yield _line("My review", Text(label, style=render.review_style(label)))
            yield _line("URL", Text(pr.url, style="dim"))
        yield Footer()

"""Textual TUI: the PR list screen.

A ``DataTable`` mirrors the default CLI table. Up/down move the row cursor,
Enter opens the detail screen, ``q``/Ctrl-C quit. The list is the one already
fetched, filtered, and sorted by the CLI (fetched once at startup).
"""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header

from cubrid_dev2_pr import render, review
from cubrid_dev2_pr.models import PullRequest
from cubrid_dev2_pr.tui.detail import DetailScreen


class PrListApp(App[None]):
    """Top-level TUI app showing the teammate PR list."""

    TITLE = "cubrid-dev2-pr"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, prs: list[PullRequest], repo: str, reviewer: str) -> None:
        super().__init__()
        self._prs = prs
        self._repo = repo
        self._reviewer = reviewer
        self._by_key: dict[str, PullRequest] = {str(pr.number): pr for pr in prs}

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = f"{self._repo} — reviewer: {self._reviewer}"
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("PR", "AUTHOR", "OPENED", "APPROVALS", "MY REVIEW", "TITLE")
        for pr in self._prs:
            approved, pool = review.approval_stats(pr)
            label = review.review_label(pr, self._reviewer)
            title = ("[DRAFT] " if pr.is_draft else "") + pr.title
            table.add_row(
                Text(f"#{pr.number}", style="bold"),
                Text(pr.author_login),
                Text(pr.created_at[:10]),
                Text(f"{approved}/{pool}", style=render.ratio_style(approved, pool)),
                Text(label, style=render.review_style(label)),
                Text(title),
                key=str(pr.number),
            )
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        key = event.row_key.value
        if key is None:
            return
        pr = self._by_key.get(key)
        if pr is not None:
            self.push_screen(DetailScreen(pr, self._repo, self._reviewer))


def run_tui(prs: list[PullRequest], repo: str, reviewer: str) -> None:
    """Launch the Textual app over the already-fetched, filtered PR list."""
    PrListApp(prs, repo, reviewer).run()

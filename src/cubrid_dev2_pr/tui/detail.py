"""Textual detail screen for a single PR.

Shows PR metadata, a reviewer-status list grouped by state, and the PR body
rendered as markdown. The body is fetched lazily on first open (in a thread, so
the blocking ``gh pr view`` never freezes the UI) and cached for the session.
Esc returns to the list; ``q`` quits.
"""

from __future__ import annotations

import asyncio

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Markdown, Static

from cubrid_dev2_pr import gh, render, review
from cubrid_dev2_pr.models import PullRequest

_GROUP_LABELS = [
    ("approved", "approved", "green"),
    ("changes_requested", "changes requested", "red"),
    ("commented", "commented only", "dim"),
    ("awaiting", "awaiting review", "yellow"),
]


def _line(label: str, value: Text) -> Static:
    """A bold fixed-width label followed by a (possibly styled) value."""
    return Static(Text.assemble((f"{label:<11}", "bold"), value))


class DetailScreen(Screen[None]):
    """Read-only detail view for one pull request."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(
        self,
        pr: PullRequest,
        repo: str,
        reviewer: str,
        body_cache: dict[int, str],
    ) -> None:
        super().__init__()
        self._pr = pr
        self._repo = repo
        self._reviewer = reviewer
        self._cache = body_cache

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
            yield Static("")
            yield Static(Text("Reviewers", style="bold underline"))
            yield Static(self._reviewers_text())
            yield Static("")
            yield Static(Text("Description", style="bold underline"))
            yield Markdown("_Loading…_", id="pr-body")
        yield Footer()

    def on_mount(self) -> None:
        self._load_body()

    def _reviewers_text(self) -> Text:
        groups = review.reviewer_groups(self._pr)
        out = Text()
        for key, label, style in _GROUP_LABELS:
            names = groups[key]
            if not names:
                continue
            out.append(f"{label}: ", style="bold")
            out.append(", ".join(names), style=style)
            out.append("\n")
        if not out:
            out.append("(no reviewers yet)", style="dim")
        return out

    @work(exclusive=True)
    async def _load_body(self) -> None:
        pr = self._pr
        body = self._cache.get(pr.number)
        if body is None:
            # gh is a blocking subprocess; run it off the event loop.
            body = await asyncio.to_thread(self._fetch_body)
            self._cache[pr.number] = body
        await self.query_one("#pr-body", Markdown).update(body)

    def _fetch_body(self) -> str:
        try:
            return gh.fetch_pr_detail(self._repo, self._pr.number).body or "_(no description)_"
        except gh.GhError as exc:
            return f"_Failed to load body: {exc}_"

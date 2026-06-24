"""Typed models for the GitHub PR data returned by ``gh``.

These mirror the JSON shapes produced by ``gh pr list/view --json ...`` after
light normalization (see :mod:`cubrid_dev2_pr.gh`).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Review:
    """A single review by one author at one point in time."""

    author_login: str
    state: str  # APPROVED | CHANGES_REQUESTED | COMMENTED | DISMISSED | ...
    submitted_at: str  # ISO-8601 timestamp


@dataclass(frozen=True)
class ReviewRequest:
    """An outstanding review request (user, team, or bot).

    GitHub exposes users via ``login``, teams via ``slug``, with a ``name``
    fallback; all three are normalized into :attr:`name`.
    """

    name: str


@dataclass(frozen=True)
class PullRequest:
    """An open pull request with the fields this tool displays."""

    number: int
    title: str
    url: str
    author_login: str
    is_draft: bool
    created_at: str  # ISO-8601 timestamp
    latest_reviews: list[Review] = field(default_factory=list)
    review_requests: list[ReviewRequest] = field(default_factory=list)
    body: str | None = None  # fetched lazily in TUI detail mode

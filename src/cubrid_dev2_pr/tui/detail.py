"""Textual detail screen for a single PR.

Milestone 8: shows number/title/author/opened/url/approval ratio/my review, a
reviewer-status list grouped by state, and the PR body rendered as markdown via
Textual's ``Markdown`` widget. The body is fetched lazily on first open and
cached for the session (no in-app refresh key). Esc returns to the list.
"""

from __future__ import annotations

from cubrid_dev2_pr.models import PullRequest


def load_body(repo: str, pr: PullRequest) -> str:
    """Return the PR body, fetching it lazily on first access.

    Milestone 8: call :func:`cubrid_dev2_pr.gh.fetch_pr_detail` and cache.
    """
    raise NotImplementedError("Milestone 8: lazy body fetch + cache")

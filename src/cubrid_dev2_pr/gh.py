"""Fetch PR data by shelling out to the GitHub CLI (``gh``)."""

from __future__ import annotations

from cubrid_dev2_pr.models import PullRequest

LIST_FIELDS = "number,title,url,author,isDraft,createdAt,latestReviews,reviewRequests"
DETAIL_FIELDS = "number,title,url,author,isDraft,createdAt,body,latestReviews,reviewRequests"


def ensure_gh_available() -> None:
    """Verify ``gh`` is installed and authenticated.

    Milestone 3: preflight check; raise a clear, user-facing error otherwise.
    """
    raise NotImplementedError("Milestone 3: gh availability/auth preflight")


def fetch_pr_list(repo: str, limit: int) -> list[PullRequest]:
    """Run ``gh pr list`` and parse the result into models.

    Milestone 3: subprocess call + JSON parse + reviewRequests normalization.
    """
    raise NotImplementedError("Milestone 3: gh pr list + JSON parse")


def fetch_pr_detail(repo: str, number: int) -> PullRequest:
    """Run ``gh pr view <number>`` (including body) and parse into a model.

    Milestone 3: subprocess call + JSON parse for the detail screen.
    """
    raise NotImplementedError("Milestone 3: gh pr view + JSON parse")

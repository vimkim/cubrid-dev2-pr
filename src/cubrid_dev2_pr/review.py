"""Approval / review-state semantics ported from ``cubrid-pr-check.sh``.

GitHub-style review-pool math: only the latest review per author counts; the
denominator is the union of latest-review authors and outstanding requested
reviewers (bots and non-teammates included).
"""

from __future__ import annotations

from cubrid_dev2_pr.models import PullRequest, Review

# My-review labels.
SELF_AUTHORED = "self-authored"
APPROVED = "APPROVED"
CHANGES_REQUESTED = "CHANGES_REQUESTED"
COMMENTED_ONLY = "commented only"
NOT_REVIEWED = "not reviewed"


def latest_reviews_by_author(pr: PullRequest) -> dict[str, Review]:
    """Reduce ``latest_reviews`` to the most recent review per author login.

    ``gh``'s ``latestReviews`` is meant to be one-per-author already, but we
    re-derive defensively (matching the prototype): later ``submitted_at`` wins,
    and ties resolve to the entry appearing last in the original list.
    """
    latest: dict[str, Review] = {}
    for review in pr.latest_reviews:
        previous = latest.get(review.author_login)
        if previous is None or review.submitted_at >= previous.submitted_at:
            latest[review.author_login] = review
    return latest


def approval_stats(pr: PullRequest) -> tuple[int, int]:
    """Return ``(approved_count, pool_size)`` for the PR.

    Numerator: distinct authors whose latest review state is ``APPROVED``.
    Denominator: union of latest-review authors and outstanding requested
    reviewers (deduplicated; bots and non-teammates included).
    """
    latest = latest_reviews_by_author(pr)
    requested = {req.name for req in pr.review_requests}
    pool = set(latest) | requested
    approved = {login for login, rev in latest.items() if rev.state == APPROVED}
    return len(approved), len(pool)


def reviewer_groups(pr: PullRequest) -> dict[str, list[str]]:
    """Group every reviewer by current status for the detail view.

    Keys: ``approved``, ``changes_requested``, ``commented`` (any other review
    state), and ``awaiting`` (requested reviewers with no review yet). Each list
    is sorted; bots and non-teammates are included.
    """
    latest = latest_reviews_by_author(pr)
    requested = {req.name for req in pr.review_requests}
    return {
        "approved": sorted(login for login, rev in latest.items() if rev.state == APPROVED),
        "changes_requested": sorted(
            login for login, rev in latest.items() if rev.state == CHANGES_REQUESTED
        ),
        "commented": sorted(
            login for login, rev in latest.items() if rev.state not in (APPROVED, CHANGES_REQUESTED)
        ),
        "awaiting": sorted(name for name in requested if name not in latest),
    }


def review_label(pr: PullRequest, reviewer: str) -> str:
    """Return the configured reviewer's my-review label.

    ``self-authored`` when the PR is the reviewer's own; otherwise the
    reviewer's latest review state mapped to APPROVED / CHANGES_REQUESTED /
    ``commented only``, or ``not reviewed`` when they have no review.
    """
    if pr.author_login == reviewer:
        return SELF_AUTHORED
    latest = latest_reviews_by_author(pr).get(reviewer)
    if latest is None:
        return NOT_REVIEWED
    if latest.state == APPROVED:
        return APPROVED
    if latest.state == CHANGES_REQUESTED:
        return CHANGES_REQUESTED
    return COMMENTED_ONLY

"""Approval / review-state semantics ported from ``cubrid-pr-check.sh``.

GitHub-style review-pool math: only the latest review per author counts; the
denominator is the union of latest-review authors and outstanding requested
reviewers (bots and non-teammates included).
"""

from __future__ import annotations

from cubrid_dev2_pr.models import PullRequest

# My-review labels.
SELF_AUTHORED = "self-authored"
APPROVED = "APPROVED"
CHANGES_REQUESTED = "CHANGES_REQUESTED"
COMMENTED_ONLY = "commented only"
NOT_REVIEWED = "not reviewed"


def approval_stats(pr: PullRequest) -> tuple[int, int]:
    """Return ``(approved_count, pool_size)`` for the PR.

    Milestone 4: numerator = distinct latest-review authors whose latest state
    is APPROVED; denominator = union of latest-review authors and outstanding
    requested reviewers.
    """
    raise NotImplementedError("Milestone 4: approval pool math")


def review_label(pr: PullRequest, reviewer: str) -> str:
    """Return the configured reviewer's my-review label.

    Milestone 4: one of SELF_AUTHORED / APPROVED / CHANGES_REQUESTED /
    COMMENTED_ONLY / NOT_REVIEWED based on the reviewer's latest review.
    """
    raise NotImplementedError("Milestone 4: review label logic")

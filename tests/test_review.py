"""Tests for approval/review semantics (the ported jq pool math)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cubrid_dev2_pr import gh, review
from cubrid_dev2_pr.models import PullRequest, Review, ReviewRequest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _pr(
    *,
    author_login: str = "author",
    latest_reviews: list[Review] | None = None,
    review_requests: list[ReviewRequest] | None = None,
) -> PullRequest:
    return PullRequest(
        number=1,
        title="t",
        url="u",
        author_login=author_login,
        is_draft=False,
        created_at="2026-01-01T00:00:00Z",
        latest_reviews=latest_reviews or [],
        review_requests=review_requests or [],
    )


# --- fixture-driven ---


def test_approval_stats_from_fixture() -> None:
    prs = [gh.parse_pr(o) for o in _load("pr_list_sample.json")]
    # PR 5001: approvers {vimkim}; pool {vimkim, hyahong, coverage-bot, H2SU, storage-team}
    assert review.approval_stats(prs[0]) == (1, 5)
    # PR 5002: no approvals; pool {lht1199}
    assert review.approval_stats(prs[1]) == (0, 1)


def test_review_label_states_from_fixture() -> None:
    prs = [gh.parse_pr(o) for o in _load("pr_list_sample.json")]
    pr = prs[0]  # authored by hgryoo
    assert review.review_label(pr, "hgryoo") == review.SELF_AUTHORED
    assert review.review_label(pr, "vimkim") == review.APPROVED
    assert review.review_label(pr, "hyahong") == review.COMMENTED_ONLY
    assert review.review_label(pr, "nobody") == review.NOT_REVIEWED
    assert review.review_label(prs[1], "lht1199") == review.CHANGES_REQUESTED


# --- inline edge cases ---


def test_latest_review_supersedes_earlier() -> None:
    pr = _pr(
        latest_reviews=[
            Review("alice", "APPROVED", "2026-01-01T00:00:00Z"),
            Review("alice", "CHANGES_REQUESTED", "2026-01-02T00:00:00Z"),
        ],
    )
    # Approved then later requested changes -> not counted as approved.
    assert review.approval_stats(pr) == (0, 1)
    assert review.review_label(pr, "alice") == review.CHANGES_REQUESTED


def test_pool_unions_reviewers_and_requests_without_double_count() -> None:
    pr = _pr(
        latest_reviews=[Review("alice", "APPROVED", "2026-01-01T00:00:00Z")],
        review_requests=[ReviewRequest("alice"), ReviewRequest("bob")],
    )
    # alice appears in both review and request; counted once. Pool = {alice, bob}.
    assert review.approval_stats(pr) == (1, 2)


def test_bot_counts_in_denominator() -> None:
    pr = _pr(
        latest_reviews=[
            Review("alice", "APPROVED", "2026-01-01T00:00:00Z"),
            Review("coverage-bot", "COMMENTED", "2026-01-01T00:00:00Z"),
        ],
    )
    assert review.approval_stats(pr) == (1, 2)


def test_empty_pr_is_zero_over_zero() -> None:
    assert review.approval_stats(_pr()) == (0, 0)


def test_latest_reviews_by_author_dedupes() -> None:
    pr = _pr(
        latest_reviews=[
            Review("alice", "COMMENTED", "2026-01-01T00:00:00Z"),
            Review("alice", "APPROVED", "2026-01-03T00:00:00Z"),
            Review("bob", "CHANGES_REQUESTED", "2026-01-02T00:00:00Z"),
        ],
    )
    latest = review.latest_reviews_by_author(pr)
    assert set(latest) == {"alice", "bob"}
    assert latest["alice"].state == "APPROVED"

"""Tests for parsing ``gh`` JSON into typed models."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from cubrid_dev2_pr import gh

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_parse_pr_basic_fields() -> None:
    prs = [gh.parse_pr(obj) for obj in _load("pr_list_sample.json")]
    assert len(prs) == 2
    first = prs[0]
    assert first.number == 5001
    assert first.author_login == "hgryoo"
    assert first.is_draft is False
    assert first.created_at == "2026-06-20T01:02:03Z"
    assert first.body is None  # list mode omits the body


def test_parse_draft_flag() -> None:
    prs = [gh.parse_pr(obj) for obj in _load("pr_list_sample.json")]
    assert prs[1].is_draft is True
    assert prs[1].author_login == "vimkim"


def test_parse_reviews_preserves_each_review() -> None:
    pr = gh.parse_pr(_load("pr_list_sample.json")[0])
    states = {(r.author_login, r.state) for r in pr.latest_reviews}
    assert states == {
        ("vimkim", "APPROVED"),
        ("hyahong", "COMMENTED"),
        ("coverage-bot", "COMMENTED"),  # bots are kept
    }


def test_review_request_normalizes_login_then_slug() -> None:
    pr = gh.parse_pr(_load("pr_list_sample.json")[0])
    names = [req.name for req in pr.review_requests]
    # user -> login; team -> slug (preferred over the display name)
    assert names == ["H2SU", "storage-team"]


def test_parse_skips_reviews_without_author() -> None:
    obj: dict[str, Any] = {
        "number": 1,
        "title": "t",
        "url": "u",
        "author": {"login": "a"},
        "isDraft": False,
        "createdAt": "2026-01-01T00:00:00Z",
        "latestReviews": [
            {"author": {"login": None}, "state": "COMMENTED", "submittedAt": "x"},
            {"author": {"login": "real"}, "state": "APPROVED", "submittedAt": "y"},
        ],
        "reviewRequests": [],
    }
    pr = gh.parse_pr(obj)
    assert [r.author_login for r in pr.latest_reviews] == ["real"]


def test_parse_defaults_ghost_author_and_empty_collections() -> None:
    obj: dict[str, Any] = {
        "number": 7,
        "title": "t",
        "url": "u",
        "author": None,
        "isDraft": False,
        "createdAt": "z",
    }
    pr = gh.parse_pr(obj)
    assert pr.author_login == "ghost"
    assert pr.latest_reviews == []
    assert pr.review_requests == []
    assert pr.body is None


def test_ensure_gh_available_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)
    with pytest.raises(gh.GhError):
        gh.ensure_gh_available()


def test_months_ago_basic() -> None:
    assert gh.months_ago(date(2026, 6, 24), 3) == date(2026, 3, 24)


def test_months_ago_crosses_year_boundary() -> None:
    assert gh.months_ago(date(2026, 1, 15), 3) == date(2025, 10, 15)


def test_months_ago_clamps_day_to_shorter_month() -> None:
    # 3 months before May 31 lands in February, which has no 31st.
    assert gh.months_ago(date(2026, 5, 31), 3) == date(2026, 2, 28)


def test_months_ago_zero_or_negative_means_no_bound() -> None:
    assert gh.months_ago(date(2026, 6, 24), 0) is None
    assert gh.months_ago(date(2026, 6, 24), -1) is None


def test_fetch_pr_list_adds_search_when_created_since_given(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    def _fake_run(args: list[str]) -> str:
        captured.extend(args)
        return "[]"

    monkeypatch.setattr(gh, "_run_gh", _fake_run)
    gh.fetch_pr_list("ACME/widgets", 300, created_since="2026-03-24")
    assert "--search" in captured
    assert captured[captured.index("--search") + 1] == "created:>=2026-03-24 sort:created-desc"
    assert "open" in captured  # --state open still applied


def test_fetch_pr_list_omits_search_without_created_since(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    def _fake_run(args: list[str]) -> str:
        captured.extend(args)
        return "[]"

    monkeypatch.setattr(gh, "_run_gh", _fake_run)
    gh.fetch_pr_list("ACME/widgets", 300)
    assert "--search" not in captured

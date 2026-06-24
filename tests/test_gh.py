"""Tests for parsing ``gh`` JSON into typed models."""

from __future__ import annotations

import json
import shutil
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

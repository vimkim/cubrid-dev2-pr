"""Tests for the Rich table rendering (content + structure, not ANSI)."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any

from rich.console import Console

from cubrid_dev2_pr import gh, render

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _plain(prs: list[Any], reviewer: str) -> str:
    buf = StringIO()
    console = Console(file=buf, width=200, no_color=True)
    render.render(prs, reviewer, console=console)
    return buf.getvalue()


def test_render_includes_pr_rows() -> None:
    prs = [gh.parse_pr(o) for o in _load("pr_list_sample.json")]
    out = _plain(prs, "vimkim")
    assert "#5001" in out
    assert "1/5" in out  # approval ratio
    assert "APPROVED" in out  # vimkim's review label on #5001
    assert "overflow" in out  # part of the PR title
    assert "pull/5001" in out  # raw URL on its own line under the title


def test_render_marks_draft_titles() -> None:
    prs = [gh.parse_pr(o) for o in _load("pr_list_sample.json")]
    out = _plain(prs, "vimkim")
    assert "[DRAFT]" in out  # #5002 is a draft


def test_render_does_not_break_on_bracketed_titles() -> None:
    # A title with bracket markup must render literally, not as a style tag.
    obj = {
        "number": 99,
        "title": "[CBRD-12345] fix the thing",
        "url": "https://example/99",
        "author": {"login": "alice"},
        "isDraft": False,
        "createdAt": "2026-02-02T00:00:00Z",
    }
    out = _plain([gh.parse_pr(obj)], "vimkim")
    assert "[CBRD-12345] fix the thing" in out


def test_render_empty_state() -> None:
    assert "No open PRs" in _plain([], "vimkim")

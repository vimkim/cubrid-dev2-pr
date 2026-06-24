"""Pilot tests for the Textual TUI (list navigation + detail screen)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from textual.widgets import DataTable

from cubrid_dev2_pr import gh
from cubrid_dev2_pr.models import PullRequest
from cubrid_dev2_pr.tui.app import PrListApp
from cubrid_dev2_pr.tui.detail import DetailScreen

FIXTURES = Path(__file__).parent / "fixtures"


def _prs() -> list[Any]:
    data = json.loads((FIXTURES / "pr_list_sample.json").read_text(encoding="utf-8"))
    return [gh.parse_pr(o) for o in data]


async def test_list_populates_all_rows() -> None:
    app = PrListApp(_prs(), "CUBRID/cubrid", "vimkim")
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.row_count == 2


async def test_enter_opens_detail_screen() -> None:
    app = PrListApp(_prs(), "CUBRID/cubrid", "vimkim")
    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert isinstance(app.screen, DetailScreen)


async def test_escape_returns_to_list() -> None:
    app = PrListApp(_prs(), "CUBRID/cubrid", "vimkim")
    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert isinstance(app.screen, DetailScreen)
        await pilot.press("escape")
        assert not isinstance(app.screen, DetailScreen)


async def test_detail_loads_and_caches_body(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_detail(repo: str, number: int) -> PullRequest:
        calls.append(number)
        return PullRequest(
            number=number,
            title="t",
            url="u",
            author_login="a",
            is_draft=False,
            created_at="2026-01-01T00:00:00Z",
            body="## Title\nHello body",
        )

    monkeypatch.setattr(gh, "fetch_pr_detail", fake_detail)
    app = PrListApp(_prs(), "CUBRID/cubrid", "vimkim")
    async with app.run_test() as pilot:
        await pilot.press("enter")  # open first PR (#5001)
        await app.workers.wait_for_complete()
        assert app._body_cache[5001] == "## Title\nHello body"
        # reopen the same PR -> served from cache, no second gh call
        await pilot.press("escape")
        await pilot.press("enter")
        await app.workers.wait_for_complete()
    assert calls == [5001]

"""Integration tests for the CLI wiring (flags, filtering, precedence)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from cubrid_dev2_pr import cli, config, gh

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def _sample_prs() -> list[Any]:
    data = json.loads((FIXTURES / "pr_list_sample.json").read_text(encoding="utf-8"))
    return [gh.parse_pr(o) for o in data]


def _stub_backend(
    monkeypatch: pytest.MonkeyPatch,
    teammates: list[str],
    cfg: config.Config | None = None,
) -> dict[str, Any]:
    """Stub out gh + config, returning a dict that records the fetch call args."""
    calls: dict[str, Any] = {}

    def _fake_fetch(repo: str, limit: int, created_since: str | None = None) -> list[Any]:
        calls.update(repo=repo, limit=limit, created_since=created_since)
        return _sample_prs()

    monkeypatch.setenv("COLUMNS", "200")  # avoid table truncation in captured output
    monkeypatch.setattr(gh, "ensure_gh_available", lambda: None)
    monkeypatch.setattr(gh, "fetch_pr_list", _fake_fetch)
    resolved = cfg if cfg is not None else config.Config(teammates=teammates)
    monkeypatch.setattr(config, "load_config", lambda: resolved)
    return calls


def test_version(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_backend(monkeypatch, ["hgryoo"])
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "cubrid-dev2-pr" in result.output


def test_default_lists_teammates_and_hides_drafts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_backend(monkeypatch, ["hgryoo", "vimkim"])
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 0
    assert "#5001" in result.output  # hgryoo, not draft -> shown
    assert "#5002" not in result.output  # vimkim draft -> hidden by default


def test_drafts_flag_includes_drafts(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_backend(monkeypatch, ["hgryoo", "vimkim"])
    result = runner.invoke(cli.app, ["--drafts"])
    assert result.exit_code == 0
    assert "#5002" in result.output


def test_since_months_default_passes_a_cutoff_date(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = config.Config(teammates=["hgryoo"], since_months=3)
    calls = _stub_backend(monkeypatch, [], cfg=cfg)
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 0
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", calls["created_since"])  # YYYY-MM-DD
    assert "(since " in result.output


def test_since_months_zero_disables_date_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = config.Config(teammates=["hgryoo"], since_months=0)
    calls = _stub_backend(monkeypatch, [], cfg=cfg)
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 0
    assert calls["created_since"] is None
    assert "(since " not in result.output


def test_since_months_flag_overrides_config(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = config.Config(teammates=["hgryoo"], since_months=12)
    calls = _stub_backend(monkeypatch, [], cfg=cfg)
    result = runner.invoke(cli.app, ["--since-months", "0"])
    assert result.exit_code == 0
    assert calls["created_since"] is None  # flag (0) beats config (12)


def test_non_teammate_authors_filtered_out(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_backend(monkeypatch, ["someone-else"])
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 0
    assert "#5001" not in result.output
    assert "No open PRs" in result.output


def test_gh_error_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_backend(monkeypatch, ["hgryoo"])

    def _boom() -> None:
        raise gh.GhError("gh not authenticated")

    monkeypatch.setattr(gh, "ensure_gh_available", _boom)
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 1

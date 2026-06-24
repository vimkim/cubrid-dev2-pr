"""Integration tests for the CLI wiring (flags, filtering, precedence)."""

from __future__ import annotations

import json
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


def _stub_backend(monkeypatch: pytest.MonkeyPatch, teammates: list[str]) -> None:
    monkeypatch.setenv("COLUMNS", "200")  # avoid table truncation in captured output
    monkeypatch.setattr(gh, "ensure_gh_available", lambda: None)
    monkeypatch.setattr(gh, "fetch_pr_list", lambda repo, limit: _sample_prs())
    monkeypatch.setattr(config, "load_config", lambda: config.Config(teammates=teammates))


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

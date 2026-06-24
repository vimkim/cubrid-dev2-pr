"""Tests for config path resolution and the seed TOML template."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from cubrid_dev2_pr import config


def test_config_path_honors_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg")
    assert config.config_path() == Path("/tmp/xdg/cubrid-dev2-pr/config.toml")


def test_config_path_falls_back_to_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: Path("/home/tester"))
    assert config.config_path() == Path("/home/tester/.config/cubrid-dev2-pr/config.toml")


def test_default_config_toml_round_trips() -> None:
    data = tomllib.loads(config.default_config_toml())
    assert data["repo"] == config.DEFAULT_REPO
    assert data["reviewer"] == config.DEFAULT_REVIEWER
    assert data["limit"] == config.DEFAULT_LIMIT
    assert set(data["teammates"]) == set(config.DEFAULT_TEAMMATES)

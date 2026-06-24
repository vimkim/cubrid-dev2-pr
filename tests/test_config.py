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
    assert data["since_months"] == config.DEFAULT_SINCE_MONTHS
    assert set(data["teammates"]) == set(config.DEFAULT_TEAMMATES)


def test_load_config_creates_seed_when_absent(tmp_path: Path) -> None:
    cfg_path = tmp_path / "nested" / "config.toml"
    cfg = config.load_config(cfg_path)
    assert cfg_path.exists()  # parent dirs created too
    assert cfg.repo == config.DEFAULT_REPO
    assert cfg.reviewer == config.DEFAULT_REVIEWER
    assert cfg.limit == config.DEFAULT_LIMIT
    assert cfg.since_months == config.DEFAULT_SINCE_MONTHS
    assert set(cfg.teammates) == set(config.DEFAULT_TEAMMATES)


def test_load_config_reads_custom_values(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        'teammates = ["alice", "bob"]\nreviewer = "alice"\nrepo = "ACME/widgets"\nlimit = 42\n',
        encoding="utf-8",
    )
    cfg = config.load_config(cfg_path)
    assert cfg.teammates == ["alice", "bob"]
    assert cfg.reviewer == "alice"
    assert cfg.repo == "ACME/widgets"
    assert cfg.limit == 42


def test_load_config_fills_missing_fields(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text('teammates = ["solo"]\n', encoding="utf-8")
    cfg = config.load_config(cfg_path)
    assert cfg.teammates == ["solo"]
    assert cfg.reviewer == config.DEFAULT_REVIEWER
    assert cfg.repo == config.DEFAULT_REPO
    assert cfg.limit == config.DEFAULT_LIMIT


def test_load_config_rejects_bad_toml(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text("this is = = not toml", encoding="utf-8")
    with pytest.raises(config.ConfigError):
        config.load_config(cfg_path)


def test_load_config_rejects_non_int_limit(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text("limit = true\n", encoding="utf-8")  # bool is not a valid int
    with pytest.raises(config.ConfigError):
        config.load_config(cfg_path)


def test_load_config_rejects_non_string_teammate(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text("teammates = [1, 2]\n", encoding="utf-8")
    with pytest.raises(config.ConfigError):
        config.load_config(cfg_path)


def test_load_config_reads_custom_since_months(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text("since_months = 6\n", encoding="utf-8")
    assert config.load_config(cfg_path).since_months == 6


def test_load_config_rejects_negative_since_months(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text("since_months = -1\n", encoding="utf-8")
    with pytest.raises(config.ConfigError):
        config.load_config(cfg_path)

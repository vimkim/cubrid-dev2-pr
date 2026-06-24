"""Configuration loading and first-run bootstrap.

The config is a TOML file at ``$XDG_CONFIG_HOME/cubrid-dev2-pr/config.toml``
(falling back to ``~/.config/...``). On first run it is auto-created, seeded
with the known dev2 logins. The stdlib only *reads* TOML (``tomllib``), so the
seed file is rendered from a hand-authored, commented template.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_TEAMMATES: tuple[str, ...] = (
    "hgryoo",
    "hornetmj",
    "hyahong",
    "vimkim",
    "H2SU",
    "YeunjunLee",
    "youngjun9072",
    "InChiJun",
    "lht1199",
)
DEFAULT_REVIEWER = "vimkim"
DEFAULT_REPO = "CUBRID/cubrid"
DEFAULT_LIMIT = 300
DEFAULT_SINCE_MONTHS = 3


class ConfigError(Exception):
    """Raised when the config file exists but is malformed."""


@dataclass
class Config:
    """Resolved configuration (config-file values, before CLI overrides)."""

    teammates: list[str] = field(default_factory=lambda: list(DEFAULT_TEAMMATES))
    reviewer: str = DEFAULT_REVIEWER
    repo: str = DEFAULT_REPO
    limit: int = DEFAULT_LIMIT
    since_months: int = DEFAULT_SINCE_MONTHS


def config_path() -> Path:
    """Return the config file path, honoring ``$XDG_CONFIG_HOME``."""
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "cubrid-dev2-pr" / "config.toml"


def default_config_toml() -> str:
    """Render the seed TOML written to disk on first run."""
    teammates = ",\n".join(f'  "{login}"' for login in DEFAULT_TEAMMATES)
    return (
        "# cubrid-dev2-pr configuration\n"
        "# Logins whose open PRs are tracked.\n"
        f"teammates = [\n{teammates},\n]\n\n"
        '# Whose "my review" state is shown (override with --reviewer).\n'
        f'reviewer = "{DEFAULT_REVIEWER}"\n\n'
        "# Target repository (override with --repo).\n"
        f'repo = "{DEFAULT_REPO}"\n\n'
        "# Max PRs fetched by `gh pr list` (override with --limit).\n"
        f"limit = {DEFAULT_LIMIT}\n\n"
        "# Only fetch PRs created within the last N months; 0 = no time bound\n"
        "# (override with --since-months).\n"
        f"since_months = {DEFAULT_SINCE_MONTHS}\n"
    )


def load_config(path: Path | None = None) -> Config:
    """Load config, auto-creating the seed file on first run.

    If the file is absent it (and its parent dirs) are created from
    :func:`default_config_toml`, then read back through the same parse path so
    disk and memory cannot diverge. Raises :class:`ConfigError` on malformed
    TOML or wrong field types.
    """
    cfg_path = path if path is not None else config_path()
    if not cfg_path.exists():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(default_config_toml(), encoding="utf-8")
    try:
        with cfg_path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {cfg_path}: {exc}") from exc
    return _config_from_dict(data, cfg_path)


def _config_from_dict(data: dict[str, Any], source: Path) -> Config:
    """Validate a parsed TOML mapping into a :class:`Config`.

    Missing keys fall back to the module defaults; present keys must have the
    expected type (``limit`` rejects ``bool``, which is an ``int`` subclass).
    """
    teammates = data.get("teammates", list(DEFAULT_TEAMMATES))
    if not isinstance(teammates, list) or not all(isinstance(login, str) for login in teammates):
        raise ConfigError(f"{source}: 'teammates' must be a list of strings")

    reviewer = data.get("reviewer", DEFAULT_REVIEWER)
    if not isinstance(reviewer, str):
        raise ConfigError(f"{source}: 'reviewer' must be a string")

    repo = data.get("repo", DEFAULT_REPO)
    if not isinstance(repo, str):
        raise ConfigError(f"{source}: 'repo' must be a string")

    limit = data.get("limit", DEFAULT_LIMIT)
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ConfigError(f"{source}: 'limit' must be an integer")

    since_months = data.get("since_months", DEFAULT_SINCE_MONTHS)
    if isinstance(since_months, bool) or not isinstance(since_months, int) or since_months < 0:
        raise ConfigError(f"{source}: 'since_months' must be a non-negative integer (0 = no bound)")

    return Config(
        teammates=list(teammates),
        reviewer=reviewer,
        repo=repo,
        limit=limit,
        since_months=since_months,
    )

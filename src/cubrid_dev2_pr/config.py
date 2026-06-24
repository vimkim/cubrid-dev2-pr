"""Configuration loading and first-run bootstrap.

The config is a TOML file at ``$XDG_CONFIG_HOME/cubrid-dev2-pr/config.toml``
(falling back to ``~/.config/...``). On first run it is auto-created, seeded
with the known dev2 logins. The stdlib only *reads* TOML (``tomllib``), so the
seed file is rendered from a hand-authored, commented template.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

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


@dataclass
class Config:
    """Resolved configuration (config-file values, before CLI overrides)."""

    teammates: list[str] = field(default_factory=lambda: list(DEFAULT_TEAMMATES))
    reviewer: str = DEFAULT_REVIEWER
    repo: str = DEFAULT_REPO
    limit: int = DEFAULT_LIMIT


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
        f"limit = {DEFAULT_LIMIT}\n"
    )


def load_config(path: Path | None = None) -> Config:
    """Load config, creating the seed file on first run.

    Milestone 2: read TOML via ``tomllib``, auto-create from
    :func:`default_config_toml` when absent, and validate fields.
    """
    raise NotImplementedError("Milestone 2: TOML load + first-run create")

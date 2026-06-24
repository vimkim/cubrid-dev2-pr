"""Smoke tests confirming the scaffold imports and exposes a version."""

from __future__ import annotations

import cubrid_dev2_pr
from cubrid_dev2_pr import cli


def test_version_is_set() -> None:
    assert cubrid_dev2_pr.__version__ == "0.1.0"


def test_cli_app_is_constructed() -> None:
    # The Typer app and its entry point exist and are wired up.
    assert cli.app is not None
    assert callable(cli.run)

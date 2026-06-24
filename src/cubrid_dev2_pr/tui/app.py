"""Textual TUI entry point: the PR list screen.

Milestone 7: a Textual ``App`` with a ``DataTable`` mirroring the default table;
up/down to move, Enter to open the detail screen, ``q``/Ctrl-C to quit. The list
is fetched once at startup.
"""

from __future__ import annotations

from cubrid_dev2_pr.config import Config


def run_tui(config: Config, repo: str, reviewer: str, include_drafts: bool) -> None:
    """Launch the Textual app.

    Milestone 7: build and run the App; Milestone 8 adds the detail screen.
    """
    raise NotImplementedError("Milestone 7: Textual list screen")

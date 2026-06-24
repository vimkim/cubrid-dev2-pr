"""Regenerate the README screenshot (``docs/images/screenshot.svg``).

Mirrors :func:`cubrid_dev2_pr.cli.main`'s default (non-TUI) data flow — load
config, fetch open PRs via ``gh``, keep configured teammates, hide drafts, sort
newest-first — but renders into a *recording* Rich ``Console`` so the styled
table can be exported as a faithful, text-based SVG. No terminal, screenshot
tool, or external rasterizer is involved; only ``gh`` (authenticated) and the
project's own runtime dependencies.

Usage (via the justfile)::

    just screenshot          # all teammate PRs
    just screenshot 12       # cap at the 12 most recent rows

Run directly with ``uv run python scripts/screenshot.py [ROWS] [OUT_PATH]``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from cubrid_dev2_pr import config, gh, render

DEFAULT_OUT = Path("docs/images/screenshot.svg")
CONSOLE_WIDTH = 120


def main(argv: list[str]) -> int:
    """Fetch live PRs and write the rendered table to an SVG."""
    max_rows = int(argv[0]) if len(argv) > 0 and argv[0] else 0
    out_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT

    cfg = config.load_config()
    gh.ensure_gh_available()
    prs = gh.fetch_pr_list(cfg.repo, cfg.limit)

    teammates = set(cfg.teammates)
    prs = [pr for pr in prs if pr.author_login in teammates and not pr.is_draft]
    prs.sort(key=lambda pr: pr.created_at, reverse=True)

    total = len(prs)
    if max_rows and total > max_rows:
        prs = prs[:max_rows]

    console = Console(record=True, width=CONSOLE_WIDTH)
    header = (
        f"Open PRs in {cfg.repo} from configured teammates — "
        f"reviewer: {cfg.reviewer}  (drafts hidden; use --drafts)"
    )
    console.print(header)
    render.render(prs, cfg.reviewer, console=console)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    console.save_svg(str(out_path), title="cubrid-dev2-pr")
    print(f"Rendered {len(prs)} of {total} teammate PR(s) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

# v0.1.0

First release of cubrid-dev2-pr — a CLI/TUI for tracking open CUBRID dev2
teammate PRs with review and approval state. Replaces the cubrid-pr-check.sh
prototype (behaviorally cross-validated on live data) and adds a TUI.

## Features
- Colored table of open teammate PRs: number, author, opened date, approval
  ratio, your review state, title + URL.
- GitHub-style approval pool math (latest review per author; bots included).
- TUI (`--tui`): navigable list + detail screen with lazily-fetched,
  markdown-rendered PR body and grouped reviewer-status list.
- TOML config auto-created on first run (teammates, reviewer, repo, limit).
- `gh` as the data source — no token handling in the tool.

## Install
See docs/INSTALL.md. Quick path:
`uv tool install git+https://github.com/vimkim/cubrid-dev2-pr.git`

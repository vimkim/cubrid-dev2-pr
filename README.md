# cubrid-dev2-pr

A CLI/TUI for tracking open pull requests in `CUBRID/cubrid` from the dev2
teammate set — with approval progress, your own review state, opened date, and a
drill-down detail view.

It uses the GitHub CLI (`gh`) as its data source, so authentication and host
config stay outside this tool.

> **Status:** scaffold. The command surface, config, and package layout exist;
> the data fetch, approval semantics, table rendering, and TUI are being filled
> in per the milestones in [PLAN.md](PLAN.md).

## Requirements

- Python 3.11+
- [`gh`](https://cli.github.com/) installed and authenticated (`gh auth status`)

## Install

```bash
uv tool install .       # or: pipx install .
```

## Usage

```bash
cubrid-dev2-pr                      # open teammate PRs as a colored table
cubrid-dev2-pr --drafts             # include draft PRs
cubrid-dev2-pr --repo CUBRID/cubrid
cubrid-dev2-pr --reviewer vimkim
cubrid-dev2-pr --limit 300
cubrid-dev2-pr --tui                # interactive Textual UI
```

## Configuration

A TOML config is auto-created on first run at
`~/.config/cubrid-dev2-pr/config.toml` (honoring `$XDG_CONFIG_HOME`), seeded with
the dev2 teammate logins. It sets the teammate list plus default `reviewer`,
`repo`, and `limit`; CLI flags override these.

## Development

```bash
uv sync              # create .venv, install runtime + dev deps
uv run ruff check    # lint
uv run ruff format   # format
uv run mypy          # type-check
uv run pytest        # tests
uv run cubrid-dev2-pr --help
```

See [PLAN.md](PLAN.md) for the full design and milestone breakdown.

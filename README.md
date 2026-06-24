# cubrid-dev2-pr

A CLI/TUI for tracking open pull requests in `CUBRID/cubrid` from the dev2
teammate set — with approval progress, your own review state, opened date, and a
drill-down detail view.

It uses the GitHub CLI (`gh`) as its data source, so authentication and host
config stay outside this tool.

## Requirements

- [`uv`](https://docs.astral.sh/uv/) (installs the tool, deps, and Python)
- [`gh`](https://cli.github.com/) installed and authenticated (`gh auth status`)
- Python 3.11+ — **auto-provided by uv**; no system install required

> **Fresh machine (Rocky 8 / RHEL / Ubuntu / macOS)?** Follow
> [docs/INSTALL.md](docs/INSTALL.md) — a step-by-step guide (human- and
> AI-agent-friendly) that installs uv, gh, and the tool from scratch.
> Korean usage guide: [docs/USAGE.ko.md](docs/USAGE.ko.md).

## Install

```bash
# from a local clone
uv tool install .

# or straight from GitHub
uv tool install git+https://github.com/vimkim/cubrid-dev2-pr.git
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

In the **TUI**: ↑/↓ move the row cursor, Enter opens the PR detail (with the
body rendered as markdown, fetched on demand), Esc returns to the list, `q` or
Ctrl-C quits.

## Approval semantics

The **APPROVALS** column shows `approved / pool` using GitHub-style review-pool
math:

- Only each reviewer's **latest** review counts (a re-review supersedes earlier
  ones).
- **Numerator** = distinct reviewers whose latest review is `APPROVED`.
- **Denominator (pool)** = the deduplicated union of everyone who has left a
  latest review **and** anyone with an outstanding review request.
- Bots and non-teammates are included in both numerator and denominator.

Examples:

- 3 approvers + 6 other reviewers/requested reviewers → `3/9`.
- A reviewer who approved and **later** requested changes is *not* counted as
  approved (latest state wins).

The **MY REVIEW** column shows your own latest review state per PR — `APPROVED`,
`CHANGES_REQUESTED`, `commented only`, `not reviewed`, or `self-authored` (your
own PR). Choose whose review this tracks with `--reviewer` or the `reviewer`
config key.

## Configuration

A TOML config is auto-created on first run at
`~/.config/cubrid-dev2-pr/config.toml` (honoring `$XDG_CONFIG_HOME`), seeded with
the dev2 teammate logins. It sets the teammate list plus default `reviewer`,
`repo`, and `limit`; CLI flags override these.

```toml
teammates = ["hgryoo", "hornetmj", "hyahong", "vimkim", "..."]
reviewer  = "vimkim"          # change to your own login
repo      = "CUBRID/cubrid"
limit     = 300
```

## Development

```bash
uv sync          # create .venv, install runtime + dev deps
just check       # lint + format check + mypy (strict) + pytest
just run         # run the CLI from the local venv
just --list      # all recipes
```

Without `just`, the equivalents are `uv run ruff check`, `uv run ruff format`,
`uv run mypy`, `uv run pytest`, and `uv run cubrid-dev2-pr`.

See [PLAN.md](PLAN.md) for the full design and milestone breakdown.

# cubrid-dev2-pr Plan

## Goal

Build a standalone CLI/TUI for tracking open PRs in `CUBRID/cubrid` from the dev2
teammate set, with review state, approval progress, opened date, links, and a
drill-down view for PR details.

The existing `cubrid-pr-check.sh` dotfiles script
(`~/.config/my-scripts/bin/cubrid-pr-check.sh`) is the prototype. This project
replaces it with a richer, maintainable, **contributable** tool — the dev2 team
is expected to submit PRs against it, which is why the stack favors approachability.

## Stack

**Python 3.11+** (chosen over Rust so teammates can contribute easily; 3.11 also
gives us `tomllib` in the stdlib).

- `typer`: CLI flags, subcommand wiring, `--help`. Type-hint-driven, integrates Rich.
- `rich`: colored default table output **and** markdown rendering.
- `textual`: TUI mode (built on Rich; `DataTable` list + `Markdown` detail widget).
- `tomllib` (stdlib): read the TOML config.
- `json` (stdlib): parse `gh` JSON.
- `subprocess` (stdlib): invoke `gh`.

Models are plain `dataclasses` (stdlib, mypy-friendly). No `pydantic` unless a
later validation need justifies the dependency.

Use `gh` as the GitHub data provider. That keeps authentication, GitHub host
config, and token handling outside this tool — we only shell out and parse JSON.
`jq` is no longer needed (the prototype's jq logic is ported to Python).

## Packaging & Layout

`src/` layout, installable via `uv tool install` / `pipx` / `pip`, exposing a
`cubrid-dev2-pr` console entry point.

```
cubrid-dev2-pr/
├── pyproject.toml            # deps, [project.scripts], ruff + mypy + pytest config
├── README.md
├── PLAN.md
├── src/
│   └── cubrid_dev2_pr/
│       ├── __init__.py
│       ├── __main__.py       # `python -m cubrid_dev2_pr`
│       ├── cli.py            # Typer app; flags; default-mode vs --tui dispatch
│       ├── config.py         # load + auto-create TOML config
│       ├── gh.py             # subprocess calls to gh; JSON -> models
│       ├── models.py         # dataclasses: PullRequest, Review, ReviewRequest
│       ├── review.py         # approval semantics (the ported jq logic)
│       ├── render.py         # Rich table for default mode
│       └── tui/
│           ├── __init__.py
│           ├── app.py        # Textual App + list screen
│           └── detail.py     # detail screen (Markdown widget, lazy body)
└── tests/
    ├── fixtures/             # captured gh JSON (incl. bot + team reviewer cases)
    ├── test_review.py        # approval/label semantics
    └── test_config.py
```

## Configuration

TOML config at `~/.config/cubrid-dev2-pr/config.toml`
(honor `$XDG_CONFIG_HOME`).

**First run:** if the file is absent, auto-create it seeded with the known dev2
logins (written as a hand-authored, commented TOML template — `tomllib` only
reads), then use it.

Config controls (all overridable by CLI flags):

```toml
# cubrid-dev2-pr configuration
teammates = [
  "hgryoo", "hornetmj", "hyahong", "vimkim", "H2SU",
  "YeunjunLee", "youngjun9072", "InChiJun", "lht1199",
]
reviewer = "vimkim"          # whose "my review" state is shown
repo     = "CUBRID/cubrid"   # target repo
limit    = 300               # gh pr list --limit
```

Drafts are **not** config-driven; they stay hidden by default and are shown only
via the `--drafts` flag.

## Default CLI Mode

```bash
cubrid-dev2-pr
```

Default behavior:

- Query the configured `repo` (`CUBRID/cubrid`).
- Show open PRs authored by configured teammate logins.
- Hide draft PRs by default.
- Sort by opened date descending, newest first.
- Render a Rich colored table with columns:
  - PR number
  - author
  - opened date
  - approval stats
  - my review state
  - title
  - raw URL

Color is auto-disabled when stdout is not a TTY or `NO_COLOR` is set (Rich
`Console` default). Display states:

- `APPROVED`: green.
- `CHANGES_REQUESTED`: red.
- `commented only`: yellow or dim.
- `not reviewed`: yellow.
- `self-authored`: cyan or dim.
- Approval ratio:
  - `0/N`: red or yellow.
  - partial approval: yellow.
  - full approval: green.

URLs are printed raw (no OSC-8 clickable links).

Flags:

```bash
cubrid-dev2-pr --drafts            # include draft PRs
cubrid-dev2-pr --repo CUBRID/cubrid
cubrid-dev2-pr --reviewer vimkim
cubrid-dev2-pr --limit 300
cubrid-dev2-pr --tui               # launch the Textual TUI
```

## Approval Semantics

Ported verbatim from the prototype's jq logic. GitHub-style review-pool semantics.

For each PR:

- Numerator: distinct latest-review authors whose latest review state is `APPROVED`.
- Denominator: distinct union of latest-review authors and outstanding requested
  reviewers.
- Include bots and non-teammate reviewers in both numerator and denominator.
- For repeated reviews by the same reviewer, only the latest review state counts
  (group by author, order by `submittedAt`, take the last).
- `reviewRequests` entries are polymorphic: users expose `.login`, teams expose
  `.slug`, with a fallback to `.name`. Normalize all three when building the pool.

Examples:

- A PR with 3 approvers and 6 other reviewers/requested reviewers displays `3/9`.
- A bot comment counts in the denominator if it appears in `latestReviews`.
- A reviewer who approved and later requested changes is not counted as approved.

My-review label (for the configured `reviewer`):

- `self-authored` if the PR author is the reviewer.
- else the reviewer's latest review state mapped to:
  `APPROVED` / `CHANGES_REQUESTED` / `commented only` / `not reviewed`.

## TUI Mode

```bash
cubrid-dev2-pr --tui
```

Main screen (Textual `DataTable`):

- Show the same PR list as default CLI mode.
- Strong visual distinction for approval stats and review state.
- Up/down arrows move the selected row.
- Enter opens a detail screen for the selected PR.
- `q` or Ctrl-C quits.

Detail screen:

- Esc returns to the main PR list.
- `q` or Ctrl-C quits.
- Show:
  - PR number and title.
  - Author.
  - Opened date.
  - URL (raw).
  - Approval ratio.
  - My review state.
  - Reviewer status list.
  - PR body as the primary content, **rendered markdown** (Textual `Markdown`
    widget — headings, lists, code blocks, links styled).

Reviewer status list:

- Group reviewers by status:
  - approved
  - changes requested
  - commented only
  - review requested / no review yet
- Include bots and non-teammate reviewers.
- Only the latest review state per reviewer is displayed.

Caching / freshness:

- Fetch the PR list once at startup.
- Fetch each PR body lazily when its detail screen is first opened, then cache
  it for the session. Re-entering a PR is instant.
- No in-app refresh key; restart to refresh (a refresh key can be added later).

## Data Fetch Plan

List mode:

```bash
gh pr list \
  --repo CUBRID/cubrid \
  --state open \
  --limit 300 \
  --json number,title,url,author,isDraft,createdAt,latestReviews,reviewRequests
```

Detail mode (on demand, per selected PR):

```bash
gh pr view <number> \
  --repo CUBRID/cubrid \
  --json number,title,url,author,isDraft,createdAt,body,latestReviews,reviewRequests
```

Do not fetch PR bodies during startup. Fetch a body only for the selected PR in
TUI detail mode.

Preflight: verify `gh` is on `PATH` and emit a clear Rich-styled error if it is
missing or unauthenticated.

## Quality / Dev Tooling

- **pytest** with captured `gh` JSON fixtures in `tests/fixtures/`, focused on
  the approval/review semantics (latest-per-author pool math), including a bot
  reviewer and a team `reviewRequest` (`.slug`) case.
- **ruff** for lint + format, configured in `pyproject.toml`.
- **Type hints throughout, checked with mypy.**
- CI workflow (GitHub Actions running tests/lint on PRs) is deferred — add once
  the package layout settles.

## Milestones

1. Scaffold the Python package: `pyproject.toml`, `src/` layout, entry point,
   ruff/mypy/pytest config.
2. Implement config load + first-run auto-create (TOML).
3. Implement `gh` subprocess fetch and typed dataclass parsing (incl.
   polymorphic `reviewRequests`).
4. Port approval semantics, teammate/draft filtering, opened-date sorting, and
   the my-review label — with pytest fixtures.
5. Implement the Rich colored default-table output.
6. Wire Typer flags: `--drafts`, `--repo`, `--reviewer`, `--limit`, `--tui`.
7. Implement the Textual TUI list screen.
8. Implement the Textual detail screen with lazy, cached PR-body fetch and
   rendered markdown.
9. Add README usage examples and document the approval semantics + config.

## Resolved Decisions

- Language: **Python 3.11+** (over Rust, for contributor accessibility).
- CLI: **Typer**; output: **Rich**; TUI: **Textual**.
- Packaging: **pyproject + `src/` layout** with a `cubrid-dev2-pr` entry point.
- Teammate list (and reviewer/repo/limit defaults): **TOML config**, auto-created
  on first run.
- PR body in TUI: **rendered markdown**.
- TUI caching: **list once, detail bodies cached, no refresh key**.
- Clickable links: **raw URLs only** (OSC-8 declined).
- Tooling: **pytest + fixtures, ruff, mypy**.

## Deferred / Later

- GitHub Actions CI workflow.
- TUI in-app refresh key.
- Optional `--json` machine-readable output for scripting.
- Optional direct GitHub API client (e.g. dropping the `gh` dependency).

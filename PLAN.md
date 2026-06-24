# cubrid-dev2-pr Plan

## Goal

Build a standalone CLI/TUI for tracking open PRs in `CUBRID/cubrid` from the dev2 teammate set, with review state, approval progress, opened date, links, and a drill-down view for PR details.

The existing `cubrid-pr-check.sh` dotfiles script is the prototype. This project should replace it with a richer, maintainable tool.

## Preferred Stack

Use Rust unless a later implementation reason says otherwise.

Planned crates:

- `clap`: CLI flags and help.
- `serde`, `serde_json`: parse GitHub CLI JSON.
- `comfy-table` or `tabled`: colored default table output.
- `ratatui`, `crossterm`: TUI mode.
- `anyhow` or `miette`: user-facing errors.

Use `gh` as the GitHub data provider at first. That keeps authentication, GitHub host config, and token handling outside this tool.

## Default CLI Mode

Command:

```bash
cubrid-dev2-pr
```

Default behavior:

- Query `CUBRID/cubrid`.
- Show open PRs authored by configured teammate logins.
- Hide draft PRs by default.
- Sort by opened date descending, newest first.
- Show a colored table with:
  - PR number
  - author
  - opened date
  - approval stats
  - my review state
  - title
  - raw URL

Important display states:

- `APPROVED`: green.
- `CHANGES_REQUESTED`: red.
- `commented only`: yellow or dim.
- `not reviewed`: yellow.
- `self-authored`: cyan or dim.
- Approval ratio:
  - `0/N`: red or yellow.
  - partial approval: yellow.
  - full approval: green.

Flags:

```bash
cubrid-dev2-pr --drafts
cubrid-dev2-pr --repo CUBRID/cubrid
cubrid-dev2-pr --reviewer vimkim
cubrid-dev2-pr --tui
```

## Approval Semantics

Use GitHub-style review pool semantics.

For each PR:

- Numerator: distinct latest-review authors whose latest review state is `APPROVED`.
- Denominator: distinct union of latest-review authors and outstanding requested reviewers.
- Include bots and non-teammate reviewers in both numerator and denominator.
- For repeated reviews by the same reviewer, only the latest review state counts.

Examples:

- A PR with 3 approvers and 6 other reviewers/requested reviewers displays `3/9`.
- A bot comment counts in the denominator if it appears in `latestReviews`.
- A reviewer who approved and later requested changes is not counted as approved.

## TUI Mode

Command:

```bash
cubrid-dev2-pr --tui
```

Main screen:

- Show the same PR list as default CLI mode.
- Use strong visual distinction for approval stats and review state.
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
  - URL.
  - Approval ratio.
  - My review state.
  - Reviewer status list.
  - PR body as the primary content.

Reviewer status list:

- Group reviewers by status:
  - approved
  - changes requested
  - commented only
  - review requested / no review yet
- Include bots and non-teammate reviewers.
- Only the latest review state per reviewer should be displayed.

PR body:

- Fetch lazily when entering the detail screen.
- Display in a scrollable pane.
- Preserve markdown text enough to read checklists, links, and code blocks.

## Data Fetch Plan

List mode can call:

```bash
gh pr list \
  --repo CUBRID/cubrid \
  --state open \
  --limit 300 \
  --json number,title,url,author,isDraft,createdAt,latestReviews,reviewRequests
```

Detail mode can call on demand:

```bash
gh pr view <number> \
  --repo CUBRID/cubrid \
  --json number,title,url,author,isDraft,createdAt,body,latestReviews,reviewRequests
```

Do not fetch every PR body during startup. Fetch body only for the selected PR in TUI detail mode.

## Milestones

1. Scaffold Rust CLI.
2. Implement `gh` JSON fetch and typed parsing.
3. Port teammate filtering, draft filtering, opened-date sorting, my-review label, and approval stats.
4. Implement default colored table output.
5. Add `--drafts`, `--repo`, and `--reviewer`.
6. Implement TUI list mode.
7. Implement TUI detail screen with lazy PR body fetch.
8. Add README usage examples and approval semantics.

## Open Decisions

- Exact table library for default mode.
- Whether OSC-8 clickable terminal links are worth adding in addition to raw URLs.
- Whether to cache list/detail responses for repeated TUI navigation.
- Whether to add config file support for teammate logins later.

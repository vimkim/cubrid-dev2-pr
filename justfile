# cubrid-dev2-pr task runner. Run `just` (or `just --list`) to see recipes.
# Requires: uv (https://docs.astral.sh/uv/). Live data also needs `gh` authenticated.

set positional-arguments := true

# List available recipes
default:
    @just --list

# Create .venv and install runtime + dev dependencies
sync:
    uv sync

# Run the CLI from the local venv, e.g. `just run -- --drafts --limit 50`
run *args:
    uv run cubrid-dev2-pr "$@"

# Launch the interactive TUI
tui:
    uv run cubrid-dev2-pr --tui

# Lint with ruff (the "check" step)
lint:
    uv run ruff check

# Auto-fix lint issues, then format
fix:
    uv run ruff check --fix
    uv run ruff format

# Format the code with ruff
fmt:
    uv run ruff format

# Type-check with mypy (strict)
typecheck:
    uv run mypy

# Run the test suite, e.g. `just test -- -k config`
test *args:
    uv run pytest "$@"

# Run every CI gate locally: lint + format check + types + tests
check:
    uv run ruff check
    uv run ruff format --check
    uv run mypy
    uv run pytest

# Install as a global user tool (`cubrid-dev2-pr` on your PATH via ~/.local/bin)
install:
    uv tool install .

# Reinstall the global tool after code changes. --reinstall forces a rebuild;
# --force alone reuses uv's cached wheel because the version never changes.
reinstall:
    uv tool install --force --reinstall .

# Install with a live link to the source — no reinstall needed after .py edits
develop:
    uv tool install --force --editable .

# Remove the global tool
uninstall:
    uv tool uninstall cubrid-dev2-pr

# Remove caches and build artifacts
clean:
    rm -rf .ruff_cache .mypy_cache .pytest_cache dist build src/*.egg-info

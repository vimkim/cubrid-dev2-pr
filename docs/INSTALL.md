# Installing cubrid-dev2-pr on a fresh machine

This guide takes a **clean Linux box (Rocky/RHEL/Alma 8+, Fedora, Debian/Ubuntu)
or macOS** to a working `cubrid-dev2-pr`. It is written to be followed verbatim
by a person **or an AI coding agent** — every step is a copy-pasteable command
with a verification.

> **Maintainer prerequisite:** the repo must be pushed to GitHub and the teammate
> must have read access. Replace the URL below if your fork differs:
> `https://github.com/vimkim/cubrid-dev2-pr.git`

## What gets installed, and why

| Tool | Why | Auto-handled? |
|------|-----|---------------|
| **uv** | Installs the tool, its deps, and a suitable Python | Install once (below) |
| **Python 3.11+** | Runtime | ✅ **uv downloads a managed CPython** — you do *not* need system Python 3.11 |
| **gh** (GitHub CLI) | The data source (`gh pr list/view`) | ❌ install + authenticate (below) |
| **git** + **curl** | Clone / bootstrap | Usually present; install if missing |
| A C compiler | — | ✅ **Not needed.** The wheel is pure-Python (`py3-none-any`) |

## TL;DR (if you already have uv + an authenticated gh)

```bash
uv tool install git+https://github.com/vimkim/cubrid-dev2-pr.git
cubrid-dev2-pr --version
```

Otherwise, follow the full steps.

---

## 0. Base tools (git, curl)

```bash
# Rocky / RHEL / Alma / Fedora
sudo dnf install -y git curl

# Debian / Ubuntu
sudo apt update && sudo apt install -y git curl

# macOS (git/curl ship with the Xcode CLT; this triggers it if missing)
xcode-select --install 2>/dev/null || true
```

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Make uv available in the current shell (or open a new shell):
. "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
uv --version      # verify
```

uv installs to `~/.local/bin` (no root needed). It will fetch the right Python
automatically later — there is no separate "install Python 3.11" step.

## 2. Install gh (GitHub CLI)

Pick the path that matches your machine.

```bash
# Rocky / RHEL / Alma / Fedora (needs sudo)
sudo dnf install -y 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install -y gh

# Debian / Ubuntu (needs sudo)
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install -y gh

# macOS
brew install gh
```

### No-sudo fallback (locked-down Linux x86_64)

Drops the `gh` binary into `~/.local/bin` without root:

```bash
GH_VER=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest \
  | grep -oP '"tag_name": "v\K[^"]+')
curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_amd64.tar.gz" -o /tmp/gh.tgz
tar -xzf /tmp/gh.tgz -C /tmp
install -Dm755 "/tmp/gh_${GH_VER}_linux_amd64/bin/gh" "$HOME/.local/bin/gh"
gh --version      # verify
```

## 3. Authenticate gh

```bash
# Interactive (a human at a terminal): choose GitHub.com -> HTTPS, then a browser
# or a Personal Access Token.
gh auth login

# Non-interactive (CI, or an AI agent): use a token instead. gh reads GH_TOKEN
# automatically — no `gh auth login` needed if this is exported.
export GH_TOKEN="ghp_your_token_here"

gh auth status    # verify you are logged in and can reach github.com
```

The token needs at least the `repo` scope to read PRs and reviews.

## 4. Install the tool

```bash
# One-shot, straight from GitHub (recommended):
uv tool install git+https://github.com/vimkim/cubrid-dev2-pr.git

# …or from a local clone (for contributors):
git clone https://github.com/vimkim/cubrid-dev2-pr.git
cd cubrid-dev2-pr
uv tool install .
```

If no Python 3.11+ is present, uv downloads a managed one automatically during
this step. No compiler is invoked (pure-Python dependencies).

## 5. Make sure the command is on your PATH

```bash
uv tool update-shell      # adds ~/.local/bin to your shell profile
# then open a new shell, or:
export PATH="$HOME/.local/bin:$PATH"
```

## 6. Verify it works

```bash
cubrid-dev2-pr --version
cubrid-dev2-pr --limit 5          # should print a small colored table
```

On first run a config file is created at
`~/.config/cubrid-dev2-pr/config.toml`. **Change `reviewer` from `vimkim` to your
own GitHub login** (or pass `--reviewer YOUR_LOGIN`) so the "MY REVIEW" column
reflects *your* reviews.

---

## Notes for AI agents

- Prefer the **`GH_TOKEN` env var** over `gh auth login` — the latter is
  interactive and will hang an automated run.
- **Do not** try to install Python 3.11 via `dnf module` / `apt`; let `uv` manage
  it. Installing system Python is unnecessary and often fails on minimal images.
- All steps except the distro `gh` install are **user-level** (no root). On a box
  without sudo, use the no-sudo `gh` fallback in step 2.
- `uv tool install` is non-interactive and safe to run unattended.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv: command not found` after step 1 | `. "$HOME/.local/bin/env"` or open a new shell |
| `cubrid-dev2-pr: command not found` | `uv tool update-shell`, then re-login; or add `~/.local/bin` to PATH |
| `gh: ... authentication required` / empty results | Re-run step 3; check `gh auth status` and that the token has `repo` scope |
| Corporate proxy blocks downloads | `export HTTPS_PROXY=http://proxy:port` before curl/uv/gh commands |
| Want to update later | `uv tool upgrade cubrid-dev2-pr` (git source) or re-run `uv tool install --force .` |

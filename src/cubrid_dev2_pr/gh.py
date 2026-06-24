"""Fetch PR data by shelling out to the GitHub CLI (``gh``).

The subprocess layer (:func:`fetch_pr_list`, :func:`fetch_pr_detail`) is kept
thin; the JSON-to-model translation lives in pure functions (:func:`parse_pr`)
so it can be unit-tested against fixtures without invoking ``gh``.
"""

from __future__ import annotations

import calendar
import json
import shutil
import subprocess
from datetime import date
from typing import Any

from cubrid_dev2_pr.models import PullRequest, Review, ReviewRequest

LIST_FIELDS = "number,title,url,author,isDraft,createdAt,latestReviews,reviewRequests"
DETAIL_FIELDS = "number,title,url,author,isDraft,createdAt,body,latestReviews,reviewRequests"


class GhError(Exception):
    """Raised when ``gh`` is missing, unauthenticated, or returns an error."""


def ensure_gh_available() -> None:
    """Verify ``gh`` is installed and authenticated.

    Raises :class:`GhError` with an actionable message otherwise.
    """
    if shutil.which("gh") is None:
        raise GhError(
            "GitHub CLI `gh` was not found on PATH. Install it from https://cli.github.com/."
        )
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise GhError(f"`gh` is not authenticated. Run `gh auth login`.\n{detail}")


def _run_gh(args: list[str]) -> str:
    """Run ``gh`` with the given args and return stdout, raising on failure."""
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise GhError(
            "GitHub CLI `gh` was not found on PATH. Install it from https://cli.github.com/."
        ) from exc
    if result.returncode != 0:
        raise GhError(f"`gh {' '.join(args)}` failed:\n{result.stderr.strip()}")
    return result.stdout


def months_ago(today: date, months: int) -> date | None:
    """Return the date ``months`` calendar months before ``today``.

    Returns ``None`` when ``months <= 0`` (meaning "no time bound"). The day is
    clamped to the target month's length so e.g. three months before May 31 is
    Feb 28 (or 29), never an invalid date.
    """
    if months <= 0:
        return None
    total = (today.year * 12 + today.month - 1) - months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(today.day, last_day))


def fetch_pr_list(repo: str, limit: int, created_since: str | None = None) -> list[PullRequest]:
    """Run ``gh pr list`` for open PRs and parse the result into models.

    When ``created_since`` (a ``YYYY-MM-DD`` date) is given, GitHub's search
    ``created:>=`` qualifier filters server-side and ``sort:created-desc`` keeps
    the newest PRs when ``limit`` truncates. ``--state open`` still applies.
    """
    args = ["pr", "list", "--repo", repo, "--state", "open", "--limit", str(limit)]
    if created_since:
        args += ["--search", f"created:>={created_since} sort:created-desc"]
    args += ["--json", LIST_FIELDS]
    return [parse_pr(obj) for obj in _loads(_run_gh(args))]


def fetch_pr_detail(repo: str, number: int) -> PullRequest:
    """Run ``gh pr view <number>`` (including body) and parse into a model."""
    out = _run_gh(["pr", "view", str(number), "--repo", repo, "--json", DETAIL_FIELDS])
    return parse_pr(_loads(out))


def _loads(text: str) -> Any:
    """Parse JSON, converting decode errors into :class:`GhError`."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GhError(f"Could not parse `gh` JSON output: {exc}") from exc


def parse_pr(obj: Any) -> PullRequest:
    """Translate one decoded ``gh`` PR object into a :class:`PullRequest`."""
    author = obj.get("author") or {}
    body = obj.get("body")
    return PullRequest(
        number=int(obj["number"]),
        title=str(obj.get("title", "")),
        url=str(obj.get("url", "")),
        author_login=str(author.get("login") or "ghost"),
        is_draft=bool(obj.get("isDraft", False)),
        created_at=str(obj.get("createdAt", "")),
        latest_reviews=_parse_reviews(obj.get("latestReviews")),
        review_requests=_parse_requests(obj.get("reviewRequests")),
        body=str(body) if body is not None else None,
    )


def _parse_reviews(raw: Any) -> list[Review]:
    """Parse ``latestReviews``, skipping entries without an author login."""
    reviews: list[Review] = []
    for item in raw or []:
        author = item.get("author") or {}
        login = author.get("login")
        if not login:
            continue
        reviews.append(
            Review(
                author_login=str(login),
                state=str(item.get("state", "")),
                submitted_at=str(item.get("submittedAt", "")),
            )
        )
    return reviews


def _parse_requests(raw: Any) -> list[ReviewRequest]:
    """Parse ``reviewRequests``, normalizing user/team/bot to a single name.

    GitHub exposes users via ``login``, teams via ``slug``, with a ``name``
    fallback; the first present wins.
    """
    requests: list[ReviewRequest] = []
    for item in raw or []:
        name = item.get("login") or item.get("slug") or item.get("name")
        if not name:
            continue
        requests.append(ReviewRequest(name=str(name)))
    return requests

"""Localist daily update orchestrator.

Fetches new/active GitHub discoveries and tool releases, rewrites the README
What's New block (rolling 7-day window from seen.json history), and appends
the day's entries to the monthly news archive.

Usage:
    uv run scripts/update_news.py [--date YYYY-MM-DD] [--dry-run]

GITHUB_TOKEN is used when present; without it the script runs unauthenticated
(fine for a manual smoke run). --dry-run performs zero writes.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

import httpx

from render import (
    MarkerNotFoundError,
    append_daily_entry,
    render_news_block,
    replace_marker_block,
)
from sources.common import github_headers
from sources.github_discoveries import fetch_discoveries, load_curated_repos
from sources.tool_releases import (
    fetch_changelog_releases,
    fetch_tool_releases,
    load_watchlist,
    manual_releases,
)

HISTORY_DAYS = 7
RELEASE_WINDOW_DAYS = 7

EMPTY_SEEN = {
    "featured_repos": [],
    "releases": {},
    "changelog_pages": {},
    "history": [],
}


def build_clients(token: str | None) -> tuple[httpx.Client, httpx.Client]:
    """(github_client, page_client). The token goes ONLY on the GitHub client —
    the page client fetches third-party changelog hosts and must never carry it."""
    github = httpx.Client(
        headers=github_headers(token), timeout=30, follow_redirects=True
    )
    page = httpx.Client(
        headers={"User-Agent": "localist"}, timeout=30, follow_redirects=True
    )
    return github, page


def _load_seen(path: Path) -> dict:
    if not path.exists():
        return json.loads(json.dumps(EMPTY_SEEN))
    data = json.loads(path.read_text())
    for key, default in EMPTY_SEEN.items():
        data.setdefault(key, json.loads(json.dumps(default)))
    return data


def _archive_lines(discoveries: list[dict], releases: list[dict]) -> list[str]:
    lines = []
    for d in discoveries:
        desc = f" — {d['description']}" if d.get("description") else ""
        lines.append(f"- 🆕 [{d['name']}]({d['url']}){desc} (⭐ {d.get('stars', 0)})")
    for r in releases:
        notes = f" — {r['notes']}" if r.get("notes") else ""
        lines.append(f"- 📦 [{r['tool']} {r['version']}]({r['url']}){notes}")
    return lines


def _window_from_history(history: list[dict]) -> tuple[list[dict], list[dict]]:
    """Aggregate the 7-day window for the README block, deduped, stars-desc."""
    discoveries: dict[str, dict] = {}
    releases: dict[str, dict] = {}
    for day in history:
        for d in day.get("discoveries", []):
            discoveries.setdefault(d["name"].lower(), d)
        for r in day.get("releases", []):
            releases.setdefault(f"{r['tool']}:{r['version']}", r)
    ranked = sorted(discoveries.values(), key=lambda d: d.get("stars", 0), reverse=True)
    return ranked, list(releases.values())


def run(
    repo_root: Path,
    date: datetime.date,
    github_client: httpx.Client,
    page_client: httpx.Client,
    dry_run: bool,
) -> int:
    repo_root = Path(repo_root)
    readme_path = repo_root / "README.md"
    seen_path = repo_root / "data" / "seen.json"
    news_dir = repo_root / "news"

    tools = load_watchlist(repo_root / "data" / "watchlist.yml")
    curated = load_curated_repos(repo_root / "data" / "curated.yml")
    seen = _load_seen(seen_path)

    # ── fetch (each source isolated; failures log and continue) ──────
    discoveries = fetch_discoveries(
        github_client, date, set(seen["featured_repos"]), curated
    )
    window_start = date - datetime.timedelta(days=RELEASE_WINDOW_DAYS)
    releases = (
        fetch_tool_releases(tools, github_client, seen["releases"], window_start)
        + fetch_changelog_releases(tools, page_client, seen["changelog_pages"])
        + manual_releases(tools, seen["changelog_pages"])
    )

    # ── update state (in memory) ─────────────────────────────────────
    if discoveries or releases:
        seen["history"].append(
            {"date": date.isoformat(), "discoveries": discoveries, "releases": releases}
        )
    cutoff = (date - datetime.timedelta(days=HISTORY_DAYS - 1)).isoformat()
    seen["history"] = [h for h in seen["history"] if h["date"] >= cutoff]

    for d in discoveries:
        seen["featured_repos"].append(d["name"].lower())
    for r in releases:
        if r.get("repo"):
            seen["releases"].setdefault(r["repo"], []).append(r["version"])
        else:
            key = next(
                (t["url"] for t in tools if t.get("source") == "changelog_page" and t["name"] == r["tool"]),
                r["tool"],
            )
            seen["changelog_pages"][key] = r["version"]

    # ── render ───────────────────────────────────────────────────────
    win_disc, win_rel = _window_from_history(seen["history"])
    block = render_news_block(win_disc, win_rel, date)

    try:
        new_readme = replace_marker_block(readme_path.read_text(), block)
    except MarkerNotFoundError as exc:
        print(f"[update_news] FATAL: {exc}", file=sys.stderr)
        return 2

    if dry_run:
        print("── DRY RUN — would write README block: ──")
        print(block)
        print(f"── {len(discoveries)} discoveries, {len(releases)} releases today ──")
        return 0

    readme_path.write_text(new_readme)
    append_daily_entry(news_dir, date, _archive_lines(discoveries, releases))
    seen_path.write_text(json.dumps(seen, indent=2) + "\n")

    print(
        f"[update_news] {date}: {len(discoveries)} discoveries, "
        f"{len(releases)} releases; window has {len(win_disc)}+{len(win_rel)} items"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=datetime.date.fromisoformat, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    date = args.date or datetime.datetime.now(datetime.timezone.utc).date()
    repo_root = Path(__file__).resolve().parent.parent
    github_client, page_client = build_clients(os.environ.get("GITHUB_TOKEN"))
    try:
        return run(repo_root, date, github_client, page_client, args.dry_run)
    finally:
        github_client.close()
        page_client.close()


if __name__ == "__main__":
    raise SystemExit(main())

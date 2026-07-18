"""New and active GitHub discoveries.

GitHub repository search has no star-velocity sort and no OR across topics,
so this source runs one query per topic for two windows — recently *created*
(new projects) and recently *pushed* established projects — then merges,
dedupes, filters, and caps the result. It reports "new and active" repos,
never "trending".
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import yaml

from sources.common import GITHUB_API, sanitize_text

TOPICS = ("local-ai", "local-llm", "ollama")
NEW_WINDOW_DAYS = 7
ACTIVE_WINDOW_DAYS = 2
ACTIVE_MAX_AGE_DAYS = 90  # "active" repos must also be recent — keeps out old giants
MIN_STARS_NEW = 30
MIN_STARS_ACTIVE = 500
CAP = 5


def _search_queries(today: datetime.date) -> list[dict]:
    """Build the search calls with exact ISO dates (never relative like '7d')."""
    created_after = (today - datetime.timedelta(days=NEW_WINDOW_DAYS)).isoformat()
    pushed_after = (today - datetime.timedelta(days=ACTIVE_WINDOW_DAYS)).isoformat()
    active_created_after = (
        today - datetime.timedelta(days=ACTIVE_MAX_AGE_DAYS)
    ).isoformat()
    queries = []
    for topic in TOPICS:
        queries.append(
            {
                "q": f"topic:{topic} created:>{created_after} stars:>{MIN_STARS_NEW}",
                "sort": "stars",
                "order": "desc",
                "per_page": 10,
            }
        )
        queries.append(
            {
                "q": (
                    f"topic:{topic} created:>{active_created_after} "
                    f"pushed:>{pushed_after} stars:>{MIN_STARS_ACTIVE}"
                ),
                "sort": "updated",
                "order": "desc",
                "per_page": 10,
            }
        )
    return queries


def fetch_discoveries(
    client,
    today: datetime.date,
    seen_repos: set[str],
    curated_repos: set[str],
    cap: int = CAP,
) -> list[dict]:
    """Return up to `cap` new/active repos, deduped by full name, stars-desc.

    A failing query is logged and skipped — it never blocks the other queries.
    """
    found: dict[str, dict] = {}
    for params in _search_queries(today):
        try:
            resp = client.get(f"{GITHUB_API}/search/repositories", params=params)
            resp.raise_for_status()
            items = resp.json().get("items", [])
        except Exception as exc:  # noqa: BLE001 — isolation is the contract
            print(f"[discoveries] query failed ({params['q']}): {exc}", file=sys.stderr)
            continue

        for item in items:
            full_name = item.get("full_name", "")
            key = full_name.lower()
            if not key or key in found:
                continue
            if key in seen_repos or key in curated_repos:
                continue
            found[key] = {
                "name": full_name,
                "url": item.get("html_url", ""),
                # description is anonymous, attacker-controlled text — sanitize
                # before it can enter seen.json history or any Markdown
                "description": sanitize_text(item.get("description")),
                "stars": item.get("stargazers_count", 0),
                "created_at": item.get("created_at", ""),
            }

    ranked = sorted(found.values(), key=lambda d: d["stars"], reverse=True)
    return ranked[:cap]


def load_curated_repos(curated_path: str | Path) -> set[str]:
    """Normalized lowercase owner/name set from curated.yml.

    Accepts both 'owner/name' and full github.com URLs; non-GitHub URLs
    (e.g. https://lmstudio.ai) are ignored.
    """
    data = yaml.safe_load(Path(curated_path).read_text())
    repos: set[str] = set()
    for entry in data.get("entries", []):
        ref = (entry.get("repo_or_url") or "").strip().rstrip("/")
        if not ref:
            continue
        if ref.startswith(("http://", "https://")):
            host, _, path = ref.partition("://")[2].partition("/")
            if host.lower() != "github.com":
                continue
            parts = path.split("/")
            if len(parts) < 2:
                continue
            ref = "/".join(parts[:2])
        if ref.count("/") == 1:
            repos.add(ref.lower())
    return repos

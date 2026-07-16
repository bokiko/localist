"""Tool release feed, driven by data/watchlist.yml.

This module loads and validates the watchlist. The per-source-type fetch
handlers (github_releases, changelog_page, manual) are added on top of
load_watchlist() — everything network-facing stays out of the loading layer
so it can be tested offline.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

import yaml

GITHUB_API = "https://api.github.com"

# source type -> extra keys that entry must provide
SOURCE_TYPES = {
    "github_releases": ("repo",),
    "changelog_page": ("url",),
    "manual": (),
}


class WatchlistError(ValueError):
    """Raised when data/watchlist.yml is missing or malformed."""


def load_watchlist(path: str | Path) -> list[dict]:
    """Load and validate the tool watchlist. Returns the list of tool dicts."""
    path = Path(path)
    if not path.exists():
        raise WatchlistError(f"watchlist file not found: {path}")

    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("tools"), list):
        raise WatchlistError(f"{path} must contain a top-level 'tools' list")

    tools: list[dict] = []
    for i, tool in enumerate(data["tools"]):
        if not isinstance(tool, dict) or not tool.get("name"):
            raise WatchlistError(f"{path}: tools[{i}] is missing a 'name'")
        name = tool["name"]

        source = tool.get("source")
        if source not in SOURCE_TYPES:
            raise WatchlistError(
                f"{path}: tool '{name}' has unknown source '{source}' "
                f"(expected one of: {', '.join(SOURCE_TYPES)})"
            )

        for key in SOURCE_TYPES[source]:
            if not tool.get(key):
                raise WatchlistError(
                    f"{path}: tool '{name}' with source '{source}' requires '{key}'"
                )

        skip_patterns = tool.get("skip_patterns", [])
        if not isinstance(skip_patterns, list):
            raise WatchlistError(
                f"{path}: tool '{name}' skip_patterns must be a list"
            )

        tools.append(tool)

    return tools


_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_HEADING = re.compile(r"^\s*#+\s*")
_MD_LIST_MARKER = re.compile(r"^\s*[-*]\s+")
_PR_ATTRIBUTION = re.compile(r"\bby @[\w-]+ in https?://\S+", re.IGNORECASE)
_BARE_URL = re.compile(r"https?://\S+")
# GitHub's auto-generated section headers — noise, never news
_BOILERPLATE_LINE = re.compile(
    r"^(what'?s changed|highlights|release notes|changelog)[:!.]?$", re.IGNORECASE
)
_HINT_LEFTOVER = " \t-–—:vV.()[]"


def _is_title_echo(line: str, title_hints: tuple[str, ...]) -> bool:
    """True if the line is just the release title/tag restated."""
    remainder = line.lower()
    for hint in title_hints:
        if hint:
            remainder = remainder.replace(hint.lower().lstrip("v"), "")
    return remainder.strip(_HINT_LEFTOVER) == ""


def _first_lines(
    text: str | None,
    n: int = 2,
    max_len: int = 200,
    title_hints: tuple[str, ...] = (),
) -> str:
    """First n meaningful lines of a release body, cleaned for README use.

    Beyond markdown/HTML stripping, drops boilerplate section headers
    ("What's Changed", "Highlights", ...), PR attribution + bare URLs, and
    lines that merely restate the release title. If nothing meaningful
    survives, returns "" — no note beats a junk note.
    """
    if not text:
        return ""
    cleaned: list[str] = []
    for line in text.splitlines():
        line = _MD_IMAGE.sub("", line)
        line = _HTML_TAG.sub("", line)
        line = _MD_HEADING.sub("", line)
        line = _MD_LIST_MARKER.sub("", line)
        line = _PR_ATTRIBUTION.sub("", line)
        line = _BARE_URL.sub("", line)
        line = " ".join(line.split())
        if not line or _BOILERPLATE_LINE.match(line):
            continue
        if title_hints and _is_title_echo(line, title_hints):
            continue
        cleaned.append(line)
        if len(cleaned) == n:
            break
    joined = " ".join(cleaned)
    if len(joined) > max_len:
        # truncate at the last whitespace before the cap — never mid-word
        cut = joined.rfind(" ", 0, max_len)
        joined = joined[: cut if cut > 0 else max_len].rstrip()
    return joined


def fetch_tool_releases(
    tools: list[dict],
    client,
    seen_releases: dict[str, list[str]],
    window_start: datetime.date,
) -> list[dict]:
    """Fetch new GitHub releases for every `github_releases` tool.

    Dedup is per-tag against seen_releases[repo] (a list of tag names), so
    multiple releases published close together are all surfaced. A tool whose
    request fails is logged to stderr and skipped — it never blocks the rest.
    """
    out: list[dict] = []
    for tool in tools:
        if tool.get("source") != "github_releases":
            continue
        repo = tool["repo"]
        try:
            resp = client.get(
                f"{GITHUB_API}/repos/{repo}/releases", params={"per_page": 5}
            )
            resp.raise_for_status()
            releases = resp.json()
        except Exception as exc:  # noqa: BLE001 — isolation is the contract
            print(f"[tool_releases] {tool['name']}: fetch failed: {exc}", file=sys.stderr)
            continue

        skip = [re.compile(p) for p in tool.get("skip_patterns", [])]
        seen_tags = set(seen_releases.get(repo, []))

        for rel in releases:
            tag = rel.get("tag_name", "")
            if rel.get("draft") or rel.get("prerelease"):
                continue
            if any(p.search(tag) for p in skip):
                continue
            if tag in seen_tags:
                continue
            published = rel.get("published_at") or ""
            try:
                pub_date = datetime.date.fromisoformat(published[:10])
            except ValueError:
                continue
            if pub_date < window_start:
                continue
            out.append(
                {
                    "tool": tool["name"],
                    "repo": repo,
                    "version": tag,
                    "url": rel.get("html_url", ""),
                    "notes": _first_lines(
                        rel.get("body"), title_hints=(tag, tool["name"])
                    ),
                }
            )
    return out


# LM Studio-style changelog links: /changelog/lmstudio-v0.4.13
_CHANGELOG_LINK = re.compile(r'href="(/changelog/[a-z-]+v(\d+(?:\.\d+)*))"')


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def fetch_changelog_releases(
    tools: list[dict], client, seen_pages: dict[str, str]
) -> list[dict]:
    """Best-effort scrape of `changelog_page` tools.

    The contract is: never block the run. Any failure — HTTP error, redesigned
    markup, weird versions — logs to stderr and yields nothing for that tool.
    """
    out: list[dict] = []
    for tool in tools:
        if tool.get("source") != "changelog_page":
            continue
        name, page_url = tool["name"], tool["url"]
        try:
            resp = client.get(page_url)
            resp.raise_for_status()
            matches = _CHANGELOG_LINK.findall(resp.text)
            if not matches:
                raise ValueError("no changelog version links found (markup changed?)")
            path, version = max(matches, key=lambda m: _version_key(m[1]))
        except Exception as exc:  # noqa: BLE001 — best-effort is the contract
            print(f"[changelog] {name}: skipped: {exc}", file=sys.stderr)
            continue

        if seen_pages.get(page_url) == version:
            continue

        base = page_url.split("/changelog")[0]
        out.append(
            {"tool": name, "version": version, "url": f"{base}{path}", "notes": ""}
        )
    return out


def manual_releases(tools: list[dict], seen_pages: dict[str, str]) -> list[dict]:
    """Render `manual` tools whose hand-edited `latest` block is new."""
    out: list[dict] = []
    for tool in tools:
        if tool.get("source") != "manual":
            continue
        latest = tool.get("latest")
        if not isinstance(latest, dict) or not latest.get("version"):
            continue
        if seen_pages.get(tool["name"]) == latest["version"]:
            continue
        out.append(
            {
                "tool": tool["name"],
                "version": latest["version"],
                "url": latest.get("url", ""),
                "notes": latest.get("notes", ""),
            }
        )
    return out

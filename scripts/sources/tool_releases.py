"""Tool release feed, driven by data/watchlist.yml.

This module loads and validates the watchlist. The per-source-type fetch
handlers (github_releases, changelog_page, manual) are added on top of
load_watchlist() — everything network-facing stays out of the loading layer
so it can be tested offline.
"""

from __future__ import annotations

from pathlib import Path

import yaml

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

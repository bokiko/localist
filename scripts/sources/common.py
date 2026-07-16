"""Shared helpers for GitHub API access."""

from __future__ import annotations

GITHUB_API = "https://api.github.com"


def github_headers(token: str | None) -> dict[str, str]:
    """Standard GitHub REST headers; Authorization only when a token exists.

    Use these headers ONLY on clients that talk to api.github.com — never on
    the client used for third-party changelog pages, or the token would leak.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "localist",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

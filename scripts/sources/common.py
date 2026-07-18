"""Shared helpers for GitHub API access and untrusted-text sanitization."""

from __future__ import annotations

import re

GITHUB_API = "https://api.github.com"

# Untrusted text (repo descriptions, release notes) flows into generated
# Markdown that gets auto-committed. Everything here exists to make that
# path injection-proof.
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")  # keep the label, drop the URL
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]*>")
_BARE_URL = re.compile(r"(?:https?://|www\.)\S+")
# leftovers that could interact with the README marker block
_MARKER_LIKE = re.compile(r"<!--|-->|NEWS:START|NEWS:END", re.IGNORECASE)


def sanitize_text(text: str | None, max_len: int = 200) -> str:
    """Make untrusted text safe for generated Markdown.

    Strips Markdown links (label kept) and images, HTML comments/tags, bare
    URLs, and anything resembling the NEWS markers; collapses whitespace and
    caps at a word boundary. Returns "" when nothing meaningful survives —
    an empty description beats a junk one.
    """
    if not text:
        return ""
    t = _MD_IMAGE.sub("", text)
    t = _MD_LINK.sub(r"\1", t)
    t = _HTML_COMMENT.sub("", t)
    t = _HTML_TAG.sub("", t)
    t = _BARE_URL.sub("", t)
    t = _MARKER_LIKE.sub("", t)
    t = " ".join(t.split())
    if len(t) > max_len:
        cut = t.rfind(" ", 0, max_len)
        t = t[: cut if cut > 0 else max_len].rstrip()
    return t


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

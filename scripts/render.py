"""Markdown rendering for the Localist daily update.

Three responsibilities:
  - replace_marker_block: swap the auto-generated block in README.md
  - render_news_block: turn the day's discoveries/releases into markdown
  - append_daily_entry: archive the day's entries into news/YYYY-MM.md
"""

from __future__ import annotations

import datetime
from pathlib import Path

MARKER_START = "<!-- NEWS:START -->"
MARKER_END = "<!-- NEWS:END -->"


class MarkerNotFoundError(ValueError):
    """Raised when README.md is missing the NEWS marker comments."""


def replace_marker_block(readme_text: str, block: str) -> str:
    """Replace the content between the NEWS markers, keeping the markers."""
    start = readme_text.find(MARKER_START)
    end = readme_text.find(MARKER_END)
    if start == -1 or end == -1 or end < start:
        raise MarkerNotFoundError(
            f"README is missing the {MARKER_START} / {MARKER_END} markers "
            "(NEWS: block) — cannot update the What's New section."
        )
    head = readme_text[: start + len(MARKER_START)]
    tail = readme_text[end:]
    return f"{head}\n{block.strip()}\n{tail}"


def render_news_block(
    discoveries: list[dict], releases: list[dict], date: datetime.date
) -> str:
    """Render the README What's New block for the past-7-days window."""
    lines: list[str] = [f"*Updated {date.isoformat()}*", ""]

    if not discoveries and not releases:
        lines.append(
            "*Quiet week — no notable new projects or releases. Check the "
            "[archive](news/) for recent history.*"
        )
        return "\n".join(lines)

    if discoveries:
        lines.append("**🆕 New & active projects**")
        for d in discoveries:
            desc = (d.get("description") or "").strip()
            stars = d.get("stars")
            star_txt = f" · ⭐ {stars}" if stars is not None else ""
            lines.append(f"- [{d['name']}]({d['url']}) — {desc}{star_txt}")
        lines.append("")

    if releases:
        lines.append("**📦 Tool releases**")
        for r in releases:
            notes = (r.get("notes") or "").strip()
            note_txt = f" — {notes}" if notes else ""
            lines.append(f"- [{r['tool']} {r['version']}]({r['url']}){note_txt}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def append_daily_entry(
    news_dir: Path, date: datetime.date, entries: list[str]
) -> None:
    """Append the day's entries to news/YYYY-MM.md.

    Creates the monthly file with a header when needed. Idempotent per date:
    if the file already has a section for `date`, nothing is written.
    """
    if not entries:
        return

    news_dir = Path(news_dir)
    monthly = news_dir / f"{date:%Y-%m}.md"
    date_heading = f"## {date.isoformat()}"

    if monthly.exists():
        content = monthly.read_text()
        if date_heading in content:
            return
    else:
        content = f"# News — {date:%Y-%m}\n"

    section = "\n".join([date_heading, "", *entries])
    monthly.write_text(f"{content.rstrip()}\n\n{section}\n")

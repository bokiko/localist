"""Tests for scripts/render.py — marker replacement, news rendering, archive appends."""

import datetime

import pytest

from render import (
    MarkerNotFoundError,
    append_daily_entry,
    render_news_block,
    replace_marker_block,
)

DATE = datetime.date(2026, 7, 16)

DISCOVERIES = [
    {
        "name": "someuser/coolproject",
        "url": "https://github.com/someuser/coolproject",
        "description": "A cool local AI project",
        "stars": 412,
        "created_at": "2026-07-12T08:00:00Z",
    }
]

RELEASES = [
    {
        "tool": "Ollama",
        "version": "v0.20.1",
        "url": "https://github.com/ollama/ollama/releases/tag/v0.20.1",
        "notes": "Fixes GPU detection on some cards.",
    }
]


# ── replace_marker_block ─────────────────────────────────────────────


def test_replace_marker_block_replaces_only_between_markers():
    readme = (
        "# Title\n"
        "intro text\n"
        "<!-- NEWS:START -->\n"
        "old news line 1\n"
        "old news line 2\n"
        "<!-- NEWS:END -->\n"
        "outro text\n"
    )
    result = replace_marker_block(readme, "fresh content")

    assert "fresh content" in result
    assert "old news line 1" not in result
    assert "old news line 2" not in result
    # everything outside the markers is untouched
    assert result.startswith("# Title\nintro text\n")
    assert result.endswith("outro text\n")
    # markers survive so the next run can replace again
    assert "<!-- NEWS:START -->" in result
    assert "<!-- NEWS:END -->" in result


def test_replace_marker_block_is_repeatable():
    readme = "a\n<!-- NEWS:START -->\nx\n<!-- NEWS:END -->\nb\n"
    once = replace_marker_block(readme, "first")
    twice = replace_marker_block(once, "second")
    assert "second" in twice
    assert "first" not in twice


@pytest.mark.parametrize(
    "readme",
    [
        "no markers at all\n",
        "<!-- NEWS:START -->\nonly start marker\n",
        "only end marker\n<!-- NEWS:END -->\n",
    ],
)
def test_replace_marker_block_raises_clearly_when_markers_missing(readme):
    with pytest.raises(MarkerNotFoundError) as exc:
        replace_marker_block(readme, "content")
    # error message names the marker so the failure is debuggable from CI logs
    assert "NEWS:" in str(exc.value)


# ── render_news_block ────────────────────────────────────────────────


def test_render_news_block_empty_day_is_graceful():
    block = render_news_block([], [], DATE)
    assert isinstance(block, str)
    assert block.strip() != ""  # never leaves the README section blank
    assert "2026-07-16" in block


def test_render_news_block_with_content():
    block = render_news_block(DISCOVERIES, RELEASES, DATE)
    assert "someuser/coolproject" in block
    assert "https://github.com/someuser/coolproject" in block
    assert "Ollama" in block
    assert "v0.20.1" in block
    assert "2026-07-16" in block


def test_render_news_block_discoveries_only():
    block = render_news_block(DISCOVERIES, [], DATE)
    assert "someuser/coolproject" in block
    assert "v0.20.1" not in block


# ── append_daily_entry ───────────────────────────────────────────────


def test_append_daily_entry_creates_monthly_file_with_header(tmp_path):
    news_dir = tmp_path / "news"
    news_dir.mkdir()

    append_daily_entry(news_dir, DATE, ["- first item", "- second item"])

    monthly = news_dir / "2026-07.md"
    assert monthly.exists()
    content = monthly.read_text()
    # header for the new month comes first
    assert content.startswith("# ")
    assert "2026-07" in content.splitlines()[0]
    # the dated section and items are present
    assert "2026-07-16" in content
    assert "- first item" in content
    assert "- second item" in content


def test_append_daily_entry_does_not_duplicate_same_date(tmp_path):
    news_dir = tmp_path / "news"
    news_dir.mkdir()

    append_daily_entry(news_dir, DATE, ["- first item"])
    append_daily_entry(news_dir, DATE, ["- first item"])

    content = (news_dir / "2026-07.md").read_text()
    assert content.count("2026-07-16") == 1
    assert content.count("- first item") == 1


def test_append_daily_entry_appends_new_dates_to_same_month(tmp_path):
    news_dir = tmp_path / "news"
    news_dir.mkdir()

    append_daily_entry(news_dir, datetime.date(2026, 7, 15), ["- yesterday"])
    append_daily_entry(news_dir, DATE, ["- today"])

    content = (news_dir / "2026-07.md").read_text()
    assert "2026-07-15" in content
    assert "2026-07-16" in content
    assert content.count("# News — 2026-07") == 1  # header written once


def test_append_daily_entry_skips_empty_entries(tmp_path):
    news_dir = tmp_path / "news"
    news_dir.mkdir()

    append_daily_entry(news_dir, DATE, [])

    assert not (news_dir / "2026-07.md").exists()

"""Tests for watchlist loading/validation in scripts/sources/tool_releases.py.

Loading and validation only — no network calls here.
"""

from pathlib import Path

import pytest

from sources.tool_releases import WatchlistError, load_watchlist

REPO_ROOT = Path(__file__).resolve().parent.parent


def write_watchlist(tmp_path, body: str) -> Path:
    p = tmp_path / "watchlist.yml"
    p.write_text(body)
    return p


def test_loads_the_real_repo_watchlist():
    tools = load_watchlist(REPO_ROOT / "data" / "watchlist.yml")
    assert len(tools) >= 1
    names = [t["name"] for t in tools]
    assert "Ollama" in names
    assert "LM Studio" in names


def test_valid_github_releases_tool(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - name: Ollama
    source: github_releases
    repo: ollama/ollama
""",
    )
    tools = load_watchlist(path)
    assert tools == [
        {"name": "Ollama", "source": "github_releases", "repo": "ollama/ollama"}
    ]


def test_skip_patterns_are_preserved(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - name: llama.cpp
    source: github_releases
    repo: ggml-org/llama.cpp
    skip_patterns: ["^b\\\\d+$"]
""",
    )
    (tool,) = load_watchlist(path)
    assert tool["skip_patterns"] == ["^b\\d+$"]


def test_github_releases_requires_repo(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - name: Broken
    source: github_releases
""",
    )
    with pytest.raises(WatchlistError) as exc:
        load_watchlist(path)
    assert "Broken" in str(exc.value)
    assert "repo" in str(exc.value)


def test_changelog_page_requires_url(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - name: LM Studio
    source: changelog_page
""",
    )
    with pytest.raises(WatchlistError) as exc:
        load_watchlist(path)
    assert "url" in str(exc.value)


def test_unknown_source_type_rejected(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - name: Mystery
    source: carrier_pigeon
""",
    )
    with pytest.raises(WatchlistError) as exc:
        load_watchlist(path)
    assert "carrier_pigeon" in str(exc.value)


def test_tool_without_name_rejected(tmp_path):
    path = write_watchlist(
        tmp_path,
        """
tools:
  - source: github_releases
    repo: owner/repo
""",
    )
    with pytest.raises(WatchlistError):
        load_watchlist(path)


def test_empty_or_malformed_file_rejected(tmp_path):
    path = write_watchlist(tmp_path, "not_tools: []\n")
    with pytest.raises(WatchlistError):
        load_watchlist(path)

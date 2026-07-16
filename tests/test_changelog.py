"""Tests for changelog_page and manual handlers — mocked transport, best-effort contract."""

import httpx

from sources.tool_releases import fetch_changelog_releases, manual_releases

LMSTUDIO = {
    "name": "LM Studio",
    "source": "changelog_page",
    "url": "https://lmstudio.ai/changelog",
}

PAGE_OK = """
<html><body>
<a href="/changelog/lmstudio-v0.4.13">LM Studio 0.4.13</a>
<a href="/changelog/lmstudio-v0.4.10">LM Studio 0.4.10</a>
<a href="/changelog/lmstudio-v0.4.2">LM Studio 0.4.2</a>
</body></html>
"""

PAGE_REDESIGNED = "<html><body><h1>Welcome to our new changelog!</h1></body></html>"


def client_returning(status=200, text=PAGE_OK):
    def handler(request):
        return httpx.Response(status, text=text)

    return httpx.Client(transport=httpx.MockTransport(handler))


# ── changelog_page ───────────────────────────────────────────────────


def test_new_version_detected_and_highest_wins():
    out = fetch_changelog_releases([LMSTUDIO], client_returning(), {})
    assert len(out) == 1
    r = out[0]
    assert r["tool"] == "LM Studio"
    assert r["version"] == "0.4.13"  # highest, not first-listed order dependent
    assert r["url"] == "https://lmstudio.ai/changelog/lmstudio-v0.4.13"


def test_unchanged_version_yields_nothing():
    seen = {"https://lmstudio.ai/changelog": "0.4.13"}
    out = fetch_changelog_releases([LMSTUDIO], client_returning(), seen)
    assert out == []


def test_redesigned_page_is_skipped_not_fatal(capsys):
    out = fetch_changelog_releases(
        [LMSTUDIO], client_returning(text=PAGE_REDESIGNED), {}
    )
    assert out == []
    assert "LM Studio" in capsys.readouterr().err


def test_http_error_is_skipped_not_fatal(capsys):
    out = fetch_changelog_releases([LMSTUDIO], client_returning(status=503), {})
    assert out == []
    assert "LM Studio" in capsys.readouterr().err


def test_version_comparison_is_numeric_not_lexicographic():
    page = """
    <a href="/changelog/lmstudio-v0.4.9">old</a>
    <a href="/changelog/lmstudio-v0.4.10">new</a>
    """
    out = fetch_changelog_releases([LMSTUDIO], client_returning(text=page), {})
    assert out[0]["version"] == "0.4.10"  # 0.4.10 > 0.4.9 numerically


# ── manual ───────────────────────────────────────────────────────────


def test_manual_entry_rendered_when_new():
    tool = {
        "name": "SomeTool",
        "source": "manual",
        "latest": {"version": "2.1", "url": "https://example.com/2.1", "notes": "Big update"},
    }
    out = manual_releases([tool], {})
    assert out == [
        {"tool": "SomeTool", "version": "2.1", "url": "https://example.com/2.1", "notes": "Big update"}
    ]


def test_manual_entry_silent_when_unchanged():
    tool = {
        "name": "SomeTool",
        "source": "manual",
        "latest": {"version": "2.1", "url": "https://example.com/2.1"},
    }
    out = manual_releases([tool], {"SomeTool": "2.1"})
    assert out == []


def test_manual_without_latest_block_is_silent():
    tool = {"name": "SomeTool", "source": "manual"}
    assert manual_releases([tool], {}) == []

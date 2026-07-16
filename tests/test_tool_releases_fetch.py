"""Tests for the github_releases fetch handler — httpx.MockTransport only, no network."""

import datetime
import json

import httpx

from sources.tool_releases import fetch_tool_releases

WINDOW_START = datetime.date(2026, 7, 9)  # 7 days before the 16th

OLLAMA = {"name": "Ollama", "source": "github_releases", "repo": "ollama/ollama"}
LLAMACPP = {
    "name": "llama.cpp",
    "source": "github_releases",
    "repo": "ggml-org/llama.cpp",
    "skip_patterns": ["^b\\d+$"],
}
LMSTUDIO = {"name": "LM Studio", "source": "changelog_page", "url": "https://lmstudio.ai/changelog"}


def release(tag, published="2026-07-15T10:00:00Z", draft=False, prerelease=False, body="Notes line.\nSecond line.\nThird ignored?"):
    return {
        "tag_name": tag,
        "name": tag,
        "html_url": f"https://github.com/x/x/releases/tag/{tag}",
        "published_at": published,
        "draft": draft,
        "prerelease": prerelease,
        "body": body,
    }


def client_with(routes):
    """routes: {repo: response} where response is a list (JSON) or an int (status)."""

    def handler(request: httpx.Request) -> httpx.Response:
        for repo, resp in routes.items():
            if f"/repos/{repo}/releases" in request.url.path:
                if isinstance(resp, int):
                    return httpx.Response(resp)
                return httpx.Response(200, json=resp)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_returns_new_release_with_fields():
    client = client_with({"ollama/ollama": [release("v0.20.1")]})
    out = fetch_tool_releases([OLLAMA], client, {}, WINDOW_START)
    assert len(out) == 1
    r = out[0]
    assert r["tool"] == "Ollama"
    assert r["version"] == "v0.20.1"
    assert r["url"].endswith("/v0.20.1")
    assert r["repo"] == "ollama/ollama"
    assert "Notes line." in r["notes"]
    assert "Third ignored" not in r["notes"]  # only first ~2 lines kept


def test_skips_drafts_and_prereleases():
    client = client_with(
        {
            "ollama/ollama": [
                release("v0.21.0-rc1", prerelease=True),
                release("v0.20.9-draft", draft=True),
                release("v0.20.1"),
            ]
        }
    )
    out = fetch_tool_releases([OLLAMA], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v0.20.1"]


def test_skip_patterns_filter_build_tags():
    client = client_with(
        {"ggml-org/llama.cpp": [release("b5921"), release("v1.0.0")]}
    )
    out = fetch_tool_releases([LLAMACPP], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v1.0.0"]


def test_seen_tags_are_excluded_but_new_siblings_pass():
    # two releases close together: one already seen, one new — the new one
    # must still come through (per-tag dedup, not last-tag)
    client = client_with(
        {"ollama/ollama": [release("v0.20.2"), release("v0.20.1")]}
    )
    seen = {"ollama/ollama": ["v0.20.1"]}
    out = fetch_tool_releases([OLLAMA], client, seen, WINDOW_START)
    assert [r["version"] for r in out] == ["v0.20.2"]


def test_releases_before_window_are_excluded():
    client = client_with(
        {
            "ollama/ollama": [
                release("v0.19.0", published="2026-06-01T00:00:00Z"),
                release("v0.20.1", published="2026-07-15T00:00:00Z"),
            ]
        }
    )
    out = fetch_tool_releases([OLLAMA], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v0.20.1"]


def test_one_failing_repo_does_not_block_others(capsys):
    client = client_with(
        {
            "ggml-org/llama.cpp": 500,
            "ollama/ollama": [release("v0.20.1")],
        }
    )
    out = fetch_tool_releases([LLAMACPP, OLLAMA], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v0.20.1"]
    assert "llama.cpp" in capsys.readouterr().err  # failure is logged


def test_non_github_sources_are_ignored_here():
    client = client_with({})
    out = fetch_tool_releases([LMSTUDIO], client, {}, WINDOW_START)
    assert out == []

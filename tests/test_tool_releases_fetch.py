"""Tests for the github_releases fetch handler — httpx.MockTransport only, no network."""

import datetime
import json

import httpx

from sources.tool_releases import _first_lines, fetch_tool_releases

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


def test_bad_skip_pattern_regex_skips_tool_not_run(capsys):
    # a broken regex in the watchlist must disable that one tool, not the fetch
    broken = {
        "name": "BrokenTool",
        "source": "github_releases",
        "repo": "x/broken",
        "skip_patterns": ["(["],  # invalid regex
    }
    client = client_with(
        {"x/broken": [release("v9.9.9")], "ollama/ollama": [release("v0.20.1")]}
    )
    out = fetch_tool_releases([broken, OLLAMA], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v0.20.1"]
    err = capsys.readouterr().err
    assert "BrokenTool" in err and "regex" in err.lower()


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


def test_renamed_repo_301_redirect_is_followed():
    """ComfyUI-style case: /repos/<old-name>/releases 301s to /repositories/<id>/."""
    comfy = {"name": "ComfyUI", "source": "github_releases", "repo": "comfyanonymous/ComfyUI"}

    def handler(request: httpx.Request) -> httpx.Response:
        if "/repos/comfyanonymous/ComfyUI/releases" in request.url.path:
            return httpx.Response(
                301,
                headers={"Location": "https://api.github.com/repositories/589831718/releases?per_page=5"},
            )
        if "/repositories/589831718/releases" in request.url.path:
            return httpx.Response(200, json=[release("v1.2.3")])
        return httpx.Response(404)

    # follow_redirects=True mirrors what build_clients now configures
    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    out = fetch_tool_releases([comfy], client, {}, WINDOW_START)
    assert [r["version"] for r in out] == ["v1.2.3"]


# ── _first_lines note cleanup ────────────────────────────────────────


def test_notes_drop_whats_changed_boilerplate_line():
    # "What's Changed" is GitHub's default section header — noise, not news
    body = "## What's Changed\nNew interactive agent experience"
    assert _first_lines(body) == "New interactive agent experience"


def test_notes_drop_release_notes_and_changelog_boilerplate():
    body = "# Release Notes\n## Changelog\nActual improvement described here"
    assert _first_lines(body) == "Actual improvement described here"


def test_notes_strip_leading_list_markers():
    body = "- Fixed terminal output\n* Added Vulkan backend"
    assert _first_lines(body) == "Fixed terminal output Added Vulkan backend"


def test_notes_list_marker_only_at_line_start():
    body = "Improved multi-GPU support - now 2x faster"
    assert _first_lines(body) == "Improved multi-GPU support - now 2x faster"


def test_notes_highlights_boilerplate_dropped_without_hints():
    body = "# vLLM v0.25.1\n## Highlights"
    # "Highlights" is boilerplate; the title line survives only absent hints
    assert _first_lines(body) == "vLLM v0.25.1"


def test_notes_vllm_style_title_echo_yields_empty_with_hints():
    # the whole body is just the release title + boilerplate → no note is
    # better than a junk note
    body = "# vLLM v0.25.1\n## Highlights"
    assert _first_lines(body, title_hints=("v0.25.1", "vLLM")) == ""


def test_notes_pr_line_url_noise_removed():
    # ComfyUI-style: default-generated PR line with attribution URL
    body = (
        "# What's Changed\n"
        "* Add AGENTS.md by @comfyanonymous in "
        "https://github.com/Comfy-Org/ComfyUI/pull/14696"
    )
    out = _first_lines(body, title_hints=("v0.28.0", "ComfyUI"))
    assert "http" not in out
    assert "@" not in out
    assert "Add AGENTS.md" in out


def test_notes_bare_url_only_body_yields_empty():
    body = "https://example.com/full-changelog"
    assert _first_lines(body) == ""


def test_notes_title_echo_with_tool_prefix_dropped():
    # koboldcpp bodies open with "# koboldcpp-1.117.1" — pure title echo
    body = "# koboldcpp-1.117.1\nFixed terminal output"
    out = _first_lines(body, title_hints=("v1.117.1", "KoboldCpp"))
    assert out == "Fixed terminal output"


def test_notes_strip_html_and_markdown_images():
    body = (
        '# koboldcpp-1.117.1\n'
        '<img width="420" height="350" alt="image" src="https://example.com/x.png" />\n'
        "Actual release note text here."
    )
    out = _first_lines(body)
    assert "<img" not in out
    assert "https://example.com" not in out
    assert out == "koboldcpp-1.117.1 Actual release note text here."


def test_notes_markdown_image_syntax_removed():
    body = "![screenshot](https://example.com/pic.png)\nReal text."
    assert _first_lines(body) == "Real text."


def test_notes_normal_text_preserved_and_whitespace_collapsed():
    body = "Fixes GPU   detection on\tsome cards.\nSecond line."
    assert _first_lines(body) == "Fixes GPU detection on some cards. Second line."


def test_notes_remain_length_capped():
    body = "word " * 100
    out = _first_lines(body)
    assert len(out) <= 200


def test_notes_truncation_does_not_cut_mid_word():
    # 21-char words guarantee the 200-char cap lands inside a word
    body = "supercalifragilistic " * 20
    out = _first_lines(body)
    assert len(out) <= 200
    assert out.endswith("supercalifragilistic")  # ends on a whole word
    assert set(out.split()) == {"supercalifragilistic"}  # no partial fragments
    assert out == out.rstrip()  # trimmed, no trailing whitespace

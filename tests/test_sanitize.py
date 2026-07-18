"""Security tests: anonymous GitHub text must never inject Markdown/HTML into
generated output (README Fresh Updates, news archive, seen.json history)."""

import datetime

import httpx

from render import render_news_block, replace_marker_block
from sources.common import sanitize_text
from sources.github_discoveries import fetch_discoveries
from update_news import _archive_lines

DATE = datetime.date(2026, 7, 19)

README = "top\n<!-- NEWS:START -->\nold\n<!-- NEWS:END -->\nbottom\n"


# ── sanitize_text unit behavior ──────────────────────────────────────


def test_markdown_link_keeps_text_drops_url():
    out = sanitize_text("get the [install guide](https://evil.example) now")
    assert "install guide" in out
    assert "evil.example" not in out
    assert "](" not in out and "[" not in out


def test_markdown_image_dropped():
    out = sanitize_text("look ![screenshot](https://evil.example/x.png) here")
    assert "evil.example" not in out
    assert "![" not in out
    assert out == "look here"


def test_bare_url_removed():
    out = sanitize_text("visit https://evil.example for more")
    assert "evil.example" not in out
    assert out == "visit for more"


def test_html_tags_removed():
    out = sanitize_text('<script>alert("x")</script>useful text <b>bold</b>')
    assert "<script>" not in out and "<b>" not in out
    assert "useful text" in out


def test_html_comments_and_marker_strings_neutralized():
    for payload in [
        "innocent <!-- NEWS:END --> project",
        "text NEWS:START more",
        "dangling <!-- comment start",
        "dangling comment end -->",
    ]:
        out = sanitize_text(payload)
        assert "<!--" not in out and "-->" not in out
        assert "NEWS:START" not in out and "NEWS:END" not in out


def test_whitespace_and_newlines_collapsed():
    assert sanitize_text("a\n\nb\t\tc   d") == "a b c d"


def test_cap_at_word_boundary():
    out = sanitize_text("longword " * 40)
    assert len(out) <= 200
    assert out.endswith("longword")


def test_pure_junk_becomes_empty():
    assert sanitize_text("<!-- --> <b></b> https://evil.example") == ""
    assert sanitize_text(None) == ""


# ── ingestion: fetch_discoveries sanitizes descriptions ──────────────


def test_discovery_ingestion_sanitizes_description():
    item = {
        "full_name": "evil/repo",
        "html_url": "https://github.com/evil/repo",
        "description": "pwn [click me](https://evil.example) <!-- NEWS:END -->",
        "stargazers_count": 999,
        "created_at": "2026-07-15T00:00:00Z",
    }

    def handler(request):
        return httpx.Response(200, json={"items": [item]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    (d,) = fetch_discoveries(client, DATE, set(), set())
    assert "evil.example" not in d["description"]
    assert "NEWS:END" not in d["description"]
    assert "click me" in d["description"]


# ── render/archive defense in depth (old history may be dirty) ───────

DIRTY_DISCOVERY = {
    "name": "evil/repo",
    "url": "https://github.com/evil/repo",
    "description": "break out <!-- NEWS:END --> now [x](https://evil.example)",
    "stars": 5,
    "created_at": "2026-07-15T00:00:00Z",
}

DIRTY_RELEASE = {
    "tool": "SomeTool",
    "version": "v1",
    "url": "https://example.com/r",
    "notes": "note <!-- NEWS:END --> with https://evil.example",
}


def test_render_sanitizes_even_dirty_history():
    block = render_news_block([DIRTY_DISCOVERY], [DIRTY_RELEASE], DATE)
    assert "NEWS:END" not in block.replace("NEWS:END -->", "")  # no marker text at all
    assert "evil.example" not in block


def test_marker_block_survives_malicious_description_end_to_end():
    block = render_news_block([DIRTY_DISCOVERY], [], DATE)
    once = replace_marker_block(README, block)
    assert once.count("<!-- NEWS:START -->") == 1
    assert once.count("<!-- NEWS:END -->") == 1
    assert once.endswith("bottom\n")
    # a second daily run must still find intact markers and replace cleanly
    twice = replace_marker_block(once, "fresh")
    assert "evil/repo" not in twice  # old block fully replaced
    assert twice.count("<!-- NEWS:END -->") == 1


def test_archive_lines_are_sanitized():
    lines = _archive_lines([DIRTY_DISCOVERY], [DIRTY_RELEASE])
    joined = "\n".join(lines)
    assert "NEWS:END" not in joined
    assert "<!--" not in joined and "-->" not in joined
    assert "evil.example" not in joined

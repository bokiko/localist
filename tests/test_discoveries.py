"""Tests for GitHub discoveries source + shared GitHub headers — all mocked."""

import datetime

import httpx

from sources.common import github_headers
from sources.github_discoveries import fetch_discoveries, load_curated_repos

TODAY = datetime.date(2026, 7, 16)


def repo_item(full_name, stars=100, created="2026-07-12T00:00:00Z", desc="A project"):
    return {
        "full_name": full_name,
        "html_url": f"https://github.com/{full_name}",
        "description": desc,
        "stargazers_count": stars,
        "created_at": created,
    }


def search_client(items_by_query=None, default_items=(), fail_queries=(), capture=None):
    """Mock /search/repositories. capture (list) collects the q= params seen."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert "/search/repositories" in request.url.path
        q = request.url.params.get("q", "")
        if capture is not None:
            capture.append(q)
        for frag in fail_queries:
            if frag in q:
                return httpx.Response(500)
        if items_by_query:
            for frag, items in items_by_query.items():
                if frag in q:
                    return httpx.Response(200, json={"items": items})
        return httpx.Response(200, json={"items": list(default_items)})

    return httpx.Client(transport=httpx.MockTransport(handler))


# ── github_headers ───────────────────────────────────────────────────


def test_headers_without_token():
    h = github_headers(None)
    assert h["Accept"] == "application/vnd.github+json"
    assert h["X-GitHub-Api-Version"] == "2022-11-28"
    assert h["User-Agent"] == "localist"
    assert "Authorization" not in h


def test_headers_with_token():
    h = github_headers("ghp_abc123")
    assert h["Authorization"] == "Bearer ghp_abc123"


# ── query construction ───────────────────────────────────────────────


def test_queries_use_exact_iso_dates_not_relative():
    captured = []
    fetch_discoveries(search_client(capture=captured), TODAY, set(), set())
    assert captured, "expected at least one search query"
    new_queries = [q for q in captured if "created:" in q]
    active_queries = [q for q in captured if "pushed:" in q]
    assert new_queries and active_queries
    assert all("created:>2026-07-09" in q for q in new_queries)
    assert all("pushed:>2026-07-14" in q for q in active_queries)
    assert not any("7d" in q or "2d" in q for q in captured)


# ── result handling ──────────────────────────────────────────────────


def test_returns_parsed_fields():
    client = search_client(default_items=[repo_item("someuser/coolproject", stars=412)])
    out = fetch_discoveries(client, TODAY, set(), set())
    assert out[0] == {
        "name": "someuser/coolproject",
        "url": "https://github.com/someuser/coolproject",
        "description": "A project",
        "stars": 412,
        "created_at": "2026-07-12T00:00:00Z",
    }


def test_dedupes_across_topic_queries_by_full_name():
    client = search_client(default_items=[repo_item("dup/repo")])
    out = fetch_discoveries(client, TODAY, set(), set())
    assert len(out) == 1  # same repo returned by every query, listed once


def test_excludes_seen_and_curated_case_insensitive():
    client = search_client(
        default_items=[
            repo_item("Seen/Repo"),
            repo_item("Curated/Repo"),
            repo_item("fresh/repo"),
        ]
    )
    out = fetch_discoveries(
        client, TODAY, seen_repos={"seen/repo"}, curated_repos={"curated/repo"}
    )
    assert [d["name"] for d in out] == ["fresh/repo"]


def test_caps_to_five_sorted_by_stars():
    items = [repo_item(f"user/repo{i}", stars=i * 10) for i in range(1, 9)]
    client = search_client(default_items=items)
    out = fetch_discoveries(client, TODAY, set(), set())
    assert len(out) == 5
    stars = [d["stars"] for d in out]
    assert stars == sorted(stars, reverse=True)
    assert stars[0] == 80


def test_one_failing_query_does_not_block_others(capsys):
    client = search_client(
        items_by_query={"topic:local-llm": [repo_item("ok/repo")]},
        fail_queries=("topic:local-ai",),
    )
    out = fetch_discoveries(client, TODAY, set(), set())
    assert any(d["name"] == "ok/repo" for d in out)
    assert "local-ai" in capsys.readouterr().err


# ── load_curated_repos ───────────────────────────────────────────────


def test_load_curated_repos_normalizes(tmp_path):
    p = tmp_path / "curated.yml"
    p.write_text(
        """
entries:
  - name: Ollama
    repo_or_url: Ollama/Ollama
  - name: LM Studio
    repo_or_url: https://lmstudio.ai
  - name: Open WebUI
    repo_or_url: https://github.com/Open-WebUI/Open-WebUI
"""
    )
    repos = load_curated_repos(p)
    assert repos == {"ollama/ollama", "open-webui/open-webui"}

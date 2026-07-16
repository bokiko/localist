"""End-to-end orchestrator tests — tmp repo layout, httpx.MockTransport, no network."""

import datetime
import json

import httpx
import pytest

from update_news import build_clients, run

DATE = datetime.date(2026, 7, 16)

README = (
    "# Localist\n\n"
    "## What's New\n"
    "<!-- NEWS:START -->\nplaceholder\n<!-- NEWS:END -->\n\n"
    "rest of readme\n"
)

WATCHLIST = """
tools:
  - name: Ollama
    source: github_releases
    repo: ollama/ollama
  - name: LM Studio
    source: changelog_page
    url: https://lmstudio.ai/changelog
"""

CURATED = """
entries:
  - name: Ollama
    repo_or_url: ollama/ollama
"""

EMPTY_SEEN = {
    "featured_repos": [],
    "releases": {},
    "changelog_pages": {},
    "history": [],
}

SEARCH_ITEM = {
    "full_name": "someuser/coolproject",
    "html_url": "https://github.com/someuser/coolproject",
    "description": "A cool local AI project",
    "stargazers_count": 412,
    "created_at": "2026-07-12T00:00:00Z",
}

RELEASE = {
    "tag_name": "v0.20.1",
    "html_url": "https://github.com/ollama/ollama/releases/tag/v0.20.1",
    "published_at": "2026-07-15T10:00:00Z",
    "draft": False,
    "prerelease": False,
    "body": "Fixes GPU detection.",
}

CHANGELOG_HTML = '<a href="/changelog/lmstudio-v0.4.13">LM Studio 0.4.13</a>'


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "news").mkdir()
    (tmp_path / "README.md").write_text(README)
    (tmp_path / "data" / "watchlist.yml").write_text(WATCHLIST)
    (tmp_path / "data" / "curated.yml").write_text(CURATED)
    (tmp_path / "data" / "seen.json").write_text(json.dumps(EMPTY_SEEN))
    return tmp_path


def gh_client(search_items=(SEARCH_ITEM,), releases=(RELEASE,), fail_all=False):
    def handler(request: httpx.Request) -> httpx.Response:
        if fail_all:
            return httpx.Response(500)
        if "/search/repositories" in request.url.path:
            return httpx.Response(200, json={"items": list(search_items)})
        if "/repos/" in request.url.path:
            return httpx.Response(200, json=list(releases))
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def page_client(html=CHANGELOG_HTML, record=None):
    def handler(request: httpx.Request) -> httpx.Response:
        if record is not None:
            record.append(request)
        return httpx.Response(200, text=html)

    return httpx.Client(transport=httpx.MockTransport(handler))


def snapshot(repo):
    return {
        p.relative_to(repo).as_posix(): p.read_text()
        for p in repo.rglob("*")
        if p.is_file()
    }


# ── happy path ───────────────────────────────────────────────────────


def test_full_run_updates_readme_archive_and_seen(repo):
    code = run(repo, DATE, gh_client(), page_client(), dry_run=False)
    assert code == 0

    readme = (repo / "README.md").read_text()
    assert "someuser/coolproject" in readme
    assert "v0.20.1" in readme
    assert "0.4.13" in readme
    assert "placeholder" not in readme
    assert "rest of readme" in readme

    monthly = (repo / "news" / "2026-07.md").read_text()
    assert "2026-07-16" in monthly
    assert "someuser/coolproject" in monthly

    seen = json.loads((repo / "data" / "seen.json").read_text())
    assert "someuser/coolproject" in seen["featured_repos"]
    assert seen["releases"]["ollama/ollama"] == ["v0.20.1"]
    assert seen["changelog_pages"]["https://lmstudio.ai/changelog"] == "0.4.13"
    assert seen["history"][-1]["date"] == "2026-07-16"


def test_second_run_same_day_changes_nothing(repo):
    run(repo, DATE, gh_client(), page_client(), dry_run=False)
    before = snapshot(repo)
    code = run(repo, DATE, gh_client(), page_client(), dry_run=False)
    assert code == 0
    assert snapshot(repo) == before


# ── dry run ──────────────────────────────────────────────────────────


def test_dry_run_writes_absolutely_nothing(repo, capsys):
    before = snapshot(repo)
    code = run(repo, DATE, gh_client(), page_client(), dry_run=True)
    assert code == 0
    assert snapshot(repo) == before  # README, news/, seen.json all untouched
    out = capsys.readouterr().out
    assert "someuser/coolproject" in out  # the would-be block is printed


# ── failure behavior ─────────────────────────────────────────────────


def test_missing_markers_fail_nonzero(repo, capsys):
    (repo / "README.md").write_text("# no markers here\n")
    code = run(repo, DATE, gh_client(), page_client(), dry_run=False)
    assert code != 0
    assert "NEWS:" in capsys.readouterr().err


def test_github_down_still_completes_with_changelog(repo, capsys):
    code = run(repo, DATE, gh_client(fail_all=True), page_client(), dry_run=False)
    assert code == 0
    readme = (repo / "README.md").read_text()
    assert "0.4.13" in readme  # changelog source still delivered
    assert capsys.readouterr().err  # failures were logged


def test_nothing_new_exits_zero(repo):
    empty_gh = gh_client(search_items=(), releases=())
    quiet_page = page_client(html="<html>nothing recognizable</html>")
    code = run(repo, DATE, empty_gh, quiet_page, dry_run=False)
    assert code == 0
    assert not (repo / "news" / "2026-07.md").exists()  # no empty archive entry
    assert "Quiet week" in (repo / "README.md").read_text()


# ── history window ───────────────────────────────────────────────────


def test_history_prunes_entries_older_than_seven_days(repo):
    seen = dict(EMPTY_SEEN)
    seen["history"] = [
        {
            "date": "2026-07-01",
            "discoveries": [
                {"name": "old/ancient", "url": "u", "description": "", "stars": 1, "created_at": ""}
            ],
            "releases": [],
        }
    ]
    (repo / "data" / "seen.json").write_text(json.dumps(seen))

    run(repo, DATE, gh_client(), page_client(), dry_run=False)

    new_seen = json.loads((repo / "data" / "seen.json").read_text())
    assert all(h["date"] > "2026-07-09" for h in new_seen["history"])
    assert "old/ancient" not in (repo / "README.md").read_text()


# ── client construction / token hygiene ──────────────────────────────


def test_build_clients_token_only_on_github_client():
    gh, page = build_clients("ghp_secret")
    assert gh.headers["Authorization"] == "Bearer ghp_secret"
    assert "authorization" not in {k.lower() for k in page.headers}
    gh.close(), page.close()


def test_build_clients_no_token():
    gh, page = build_clients(None)
    assert "authorization" not in {k.lower() for k in gh.headers}
    assert gh.headers["User-Agent"] == "localist"
    gh.close(), page.close()

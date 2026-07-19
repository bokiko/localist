"""Drift guards: enforce the repo's editorial and data promises in CI.

These tests pin the contracts documented in CONTRIBUTING.md and the project
doctrine: curated.yml is the single source of truth, exactly one pick per
category, the README Essentials table reflects every pick, and the generated
NEWS block markers stay intact.
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
README = (REPO / "README.md").read_text()
CURATED = yaml.safe_load((REPO / "data" / "curated.yml").read_text())

REQUIRED_FIELDS = {
    "name",
    "category",
    "pick",
    "repo_or_url",
    "license",
    "beginner_fit",
    "hardware_fit",
    "why_this_one",
    "caveats",
    "added",
}

# Picks intentionally absent from the README Essentials table.
# Add entries here ONLY with a reason — this is the documented exception list.
README_PICK_EXCEPTIONS: dict[str, str] = {}


def entries():
    return CURATED["entries"]


# ── curated.yml data contract ────────────────────────────────────────


def test_curated_parses_with_entries():
    assert isinstance(entries(), list) and len(entries()) > 0


def test_every_entry_has_required_fields():
    problems = [
        (e.get("name", f"entry #{i}"), REQUIRED_FIELDS - set(e))
        for i, e in enumerate(entries())
        if REQUIRED_FIELDS - set(e)
    ]
    assert not problems, f"entries missing fields: {problems}"


def test_exactly_one_pick_per_category():
    by_category: dict[str, list[str]] = {}
    for e in entries():
        if e["pick"]:
            by_category.setdefault(e["category"], []).append(e["name"])
    bad = {c: names for c, names in by_category.items() if len(names) != 1}
    assert not bad, f"categories without exactly one pick: {bad}"
    all_categories = {e["category"] for e in entries()}
    unpicked = all_categories - set(by_category)
    assert not unpicked, f"categories with no pick at all: {unpicked}"


# ── README reflects the picks ────────────────────────────────────────


def _reference_of(entry) -> str:
    """The string the README must contain to count as showing this entry."""
    ref = entry["repo_or_url"].rstrip("/")
    if ref.startswith(("http://", "https://")):
        return ref
    return f"github.com/{ref}"


def test_readme_essentials_contains_every_pick():
    missing = [
        e["name"]
        for e in entries()
        if e["pick"]
        and e["name"] not in README_PICK_EXCEPTIONS
        and _reference_of(e) not in README
    ]
    assert not missing, (
        f"picks not referenced in README: {missing} — add them to the "
        "Essentials table or document an exception in README_PICK_EXCEPTIONS"
    )


def test_readme_has_no_stale_comfyui_link():
    assert "comfyanonymous/ComfyUI" not in README, (
        "README links the pre-rename ComfyUI repo; use Comfy-Org/ComfyUI"
    )


# ── generated block integrity ────────────────────────────────────────


def test_news_markers_exist_exactly_once_each():
    assert README.count("<!-- NEWS:START -->") == 1
    assert README.count("<!-- NEWS:END -->") == 1
    assert README.index("<!-- NEWS:START -->") < README.index("<!-- NEWS:END -->")


# ── cross-file consistency ───────────────────────────────────────────


def test_categories_match_documented_schema():
    documented = {
        "runner",
        "desktop_gui",
        "web_ui",
        "models_general",
        "models_coding",
        "image",
        "voice_stt",
        "voice_tts",
        "rag_documents",
        "coding_assistant",
    }
    used = {e["category"] for e in entries()}
    assert used <= documented, f"undocumented categories: {used - documented}"


def test_discovery_policy_file_shape():
    policy = yaml.safe_load((REPO / "data" / "discovery.yml").read_text())
    assert isinstance(policy["render"]["max_discoveries"], int)
    assert policy["render"]["max_discoveries"] >= 1
    for key in ("require_any", "deny_unless_strong", "editorial_hold",
                "allowlist_repos", "blocklist_repos"):
        assert isinstance(policy[key], list), f"{key} must be a list"
    assert policy["require_any"], "require_any must not be empty"
    assert isinstance(policy["agent_like"]["match_any"], list)
    assert isinstance(policy["agent_like"]["require_any"], list)


def test_readme_has_feed_disclaimer_outside_markers():
    # locked decision: disclaimer sits under the Fresh updates heading,
    # BEFORE the NEWS markers, so the pipeline never rewrites it
    head, _, _ = README.partition("<!-- NEWS:START -->")
    assert "not curated recommendations" in head


def test_readme_relative_links_resolve():
    # guides/... and data/... links in README must point at real files
    for target in re.findall(r"\]\(((?:guides|data)/[^)#]+)\)", README):
        assert (REPO / target).exists(), f"README links missing file: {target}"

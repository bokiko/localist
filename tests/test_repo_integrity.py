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


# ── guides link to the glossary before they use its vocabulary ───────

# A guide that says "3-4B parameters" without ever sending the reader to the
# glossary teaches nothing: the term is defined, but not where they are. This
# guards the linking convention so it cannot rot back one guide at a time.
#
# Scope: guides/*.md MINUS glossary.md -- the glossary is the destination, so
# requiring it to link to itself is meaningless. README.md is out of scope.
#
# Counting: one failure per (file, term) at FIRST use, not per occurrence.
# Measured before the fix, the parameter pattern alone had 45 occurrences
# across 5 files -- reporting 45 items for 5 fixes is how a test gets muted.
#
# Product names are excluded on purpose. You *install* Ollama and LM Studio;
# demanding a glossary link before "Install Ollama" is noise, and noise is
# what gets a check switched off.
GLOSSARY_PRODUCTS = {"Ollama", "LM Studio", "Open WebUI", "llama.cpp"}

# Adjectives and fragments that match inside unrelated words (e.g. "mini"
# inside "phi4-mini"). Dropped rather than special-cased.
GLOSSARY_NON_TERMS = {"mini", "tiny models", "Distilled", "abliterated", "Uncensored"}

# Jargon whose ON-PAGE form differs from its glossary heading. These are NOT a
# convenience: the heading is 'Model parameters (the "B" numbers)' while every
# page writes "8B", and the length filter below drops "Q4"/"Q5"/"Q8" entirely
# because they are two characters. Delete these patterns and three glossary
# terms lose their only coverage.
GLOSSARY_PATTERNS = {
    "parameter count (3-4B, 8B, 70B)": r"(?<![\w.])\d+(?:\.\d+)?B\b",
    "quantization level (Q4, q4_K_M)": r"(?<![\w])[Qq][458](?:_[A-Za-z_]+)?\b",
    "MoE tag (30B-A3B)": r"\b\d+B-A\d+B\b",
}


def _acronym_expansion(heading: str) -> str | None:
    """'LLM (Large Language Model)' -> 'Large Language Model'.

    Only when the parenthetical's initials actually spell the token in front of
    it. Stripping every parenthetical also discarded three real aliases, so a
    guide could spell out "Mixture of Experts" and the check would not notice.
    The other five parentheticals here are glosses, not aliases -- 'the "B"
    numbers', 'e.g. q4_K_M', 'MMLU, HumanEval, ...' -- and this rule rejects
    them without needing a list of exceptions.
    """
    match = re.match(r"^\s*([A-Za-z][\w.]*)\s*\(([^)]+)\)\s*$", heading)
    if not match:
        return None
    acronym, inner = match.group(1), match.group(2).strip()
    if any(c in inner for c in '`"\u2026'):
        return None
    words = re.findall(r"[A-Za-z]+", inner)
    if len(words) < 2:
        return None
    initials = "".join(word[0] for word in words)
    return inner if initials.lower() == acronym.lower() else None


def _glossary_terms() -> list[str]:
    headings = re.findall(
        r"^\*\*([^*]+)\*\*", (REPO / "guides" / "glossary.md").read_text(), re.M
    )
    terms = set()
    for heading in headings:
        expansion = _acronym_expansion(heading)
        if expansion:
            terms.add(expansion)
        heading = re.sub(r"\(.*?\)", "", heading).replace("`", "")
        for part in heading.split("/"):
            part = re.sub(r"\s+", " ", part).strip()
            # len > 2 also drops Q4/Q5/Q8 -- see GLOSSARY_PATTERNS above
            if len(part) > 2 and part not in GLOSSARY_PRODUCTS | GLOSSARY_NON_TERMS:
                terms.add(part)
    return sorted(terms)


def _guides_to_scan():
    return sorted(
        p for p in (REPO / "guides").glob("*.md") if p.name != "glossary.md"
    )


def test_glossary_terms_are_discoverable():
    """The term list must not silently empty out if glossary.md is restructured."""
    terms = _glossary_terms()
    assert len(terms) >= 20, f"only {len(terms)} glossary terms parsed — check the headings"
    assert "VRAM" in terms and "Quantization" in terms


def test_guides_link_glossary_before_using_its_vocabulary():
    failures = []
    for path in _guides_to_scan():
        lines = path.read_text().split("\n")
        # A real markdown link, not the bare string: "[glossary](glossary.md"
        # with a missing paren reads as correct in source and renders broken.
        link_at = next(
            (
                i
                for i, line in enumerate(lines)
                if re.search(r"\]\(glossary\.md(?:#[\w-]+)?\)", line)
            ),
            None,
        )

        def first_use(pattern, flags=0):
            return next(
                (i for i, line in enumerate(lines) if re.search(pattern, line, flags)),
                None,
            )

        checks = [
            (term, r"(?<![\w`])" + re.escape(term) + r"(?![\w])", re.I)
            for term in _glossary_terms()
        ] + [(label, pattern, 0) for label, pattern in GLOSSARY_PATTERNS.items()]

        for label, pattern, flags in checks:
            used_at = first_use(pattern, flags)
            if used_at is not None and (link_at is None or link_at > used_at):
                failures.append(f"{path.name}:{used_at + 1} uses {label!r}")

    assert not failures, (
        "these guides use glossary vocabulary before linking to the glossary "
        "(add a glossary.md link at or above the line):\n  "
        + "\n  ".join(sorted(failures))
    )

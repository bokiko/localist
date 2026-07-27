"""PR-1 data contract: data/models.yml.

Validates the memory→size→examples tiers and enforces two anti-drift rules:
  1. Every example's family_ref resolves to a curated.yml model entry
     (models.yml must NOT become a second source of truth).
  2. The tier structure matches guides/choosing-models.md (the human table).
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MODELS = yaml.safe_load((REPO / "data" / "models.yml").read_text())
CURATED = yaml.safe_load((REPO / "data" / "curated.yml").read_text())
CHOOSING = (REPO / "guides" / "choosing-models.md").read_text()

MODEL_CATEGORIES = {"models_general", "models_coding"}


def _catalog():
    return {c["id"]: c for c in MODELS["catalog"]}


def _curated_model_names():
    return {
        e["name"]
        for e in CURATED["entries"]
        if e.get("category") in MODEL_CATEGORIES
    }


def _nums(text):
    """The set of integer size/memory tokens in a string, e.g. '30B–32B' -> {30,32}."""
    return {int(n) for n in re.findall(r"\d+", text)}


# ── schema ───────────────────────────────────────────────────────────────

def test_top_level_shape():
    assert MODELS.get("version") == 1
    for key in ("tiers", "catalog", "rules"):
        assert key in MODELS, f"models.yml missing '{key}'"


def test_tiers_wellformed():
    seen = set()
    for t in MODELS["tiers"]:
        for f in ("id", "basis", "memory", "size_class", "examples", "expectations"):
            assert t.get(f) not in (None, "", []), f"tier {t.get('id')} missing {f}"
        assert t["basis"] in {"vram", "ram"}, t
        assert t["id"] not in seen, f"duplicate tier id {t['id']}"
        seen.add(t["id"])


def test_catalog_wellformed():
    for c in MODELS["catalog"]:
        for f in ("id", "name", "family_ref", "why"):
            assert c.get(f), f"catalog entry missing {f}: {c}"


def test_tier_examples_exist_in_catalog():
    catalog = _catalog()
    for t in MODELS["tiers"]:
        for ex in t["examples"]:
            assert ex in catalog, f"tier {t['id']} references unknown model '{ex}'"


def test_rules_present():
    rules = MODELS["rules"]
    assert 0 < rules["fit_ratio"] <= 1
    assert 0 < rules["apple_unified_haircut"] <= 1


# ── drift check #1: models.yml ↔ curated.yml ─────────────────────────────

def test_every_catalog_family_resolves_to_curated():
    """models.yml is not a second source of truth: each example's family must
    exist in curated.yml under a model category."""
    valid = _curated_model_names()
    offenders = [
        (c["id"], c["family_ref"])
        for c in MODELS["catalog"]
        if c["family_ref"] not in valid
    ]
    assert not offenders, (
        f"catalog family_ref(s) not found in curated.yml model entries: {offenders}. "
        f"Valid names: {sorted(valid)}"
    )


# ── drift check #2: models.yml ↔ choosing-models.md ──────────────────────

def _guide_table_rows(header_contains):
    """Return the data rows of the first markdown table whose header row
    contains `header_contains`."""
    lines = CHOOSING.splitlines()
    rows = []
    in_table = False
    for line in lines:
        if header_contains in line and line.strip().startswith("|"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            if set(line.strip()) <= set("|-: "):  # separator row
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return rows


def test_vram_tiers_match_choosing_guide():
    # VRAM table header: "| Your memory | Model size that fits well | Examples |"
    rows = _guide_table_rows("Model size that fits well")
    assert rows, "could not locate the VRAM size table in choosing-models.md"
    guide_mem = {tuple(sorted(_nums(r[0]))): _nums(r[1]) for r in rows}
    # collapse to memory-number -> size tokens
    guide_by_mem = {}
    for r in rows:
        mem = min(_nums(r[0])) if _nums(r[0]) else None
        if mem is not None:
            guide_by_mem[mem] = _nums(r[1])

    yaml_vram = {
        min(_nums(t["memory"])): _nums(t["size_class"])
        for t in MODELS["tiers"]
        if t["basis"] == "vram"
    }
    assert set(yaml_vram) == set(guide_by_mem), (
        f"VRAM memory tiers differ. yaml={sorted(yaml_vram)} guide={sorted(guide_by_mem)}"
    )
    for mem, guide_sizes in guide_by_mem.items():
        assert guide_sizes <= yaml_vram[mem], (
            f"{mem}GB size class drifted: guide {guide_sizes} not covered by "
            f"yaml {yaml_vram[mem]}"
        )


def test_ram_tiers_match_mac_table():
    # Mac table header: "| Mac RAM | Realistic room for models | Comfortable class |"
    rows = _guide_table_rows("Comfortable class")
    assert rows, "could not locate the Mac RAM table in choosing-models.md"
    guide_by_mem = {}
    for r in rows:
        mem = min(_nums(r[0])) if _nums(r[0]) else None
        if mem is not None:
            guide_by_mem[mem] = _nums(r[2])  # comfortable class column

    yaml_ram = {
        min(_nums(t["memory"])): _nums(t["size_class"])
        for t in MODELS["tiers"]
        if t["basis"] == "ram"
    }
    assert set(yaml_ram) == set(guide_by_mem), (
        f"RAM memory tiers differ. yaml={sorted(yaml_ram)} guide={sorted(guide_by_mem)}"
    )
    for mem, guide_sizes in guide_by_mem.items():
        assert guide_sizes <= yaml_ram[mem], (
            f"{mem}GB Mac class drifted: guide {guide_sizes} not covered by "
            f"yaml {yaml_ram[mem]}"
        )

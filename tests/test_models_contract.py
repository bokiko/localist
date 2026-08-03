"""PR-1 data contract: data/models.yml.

Validates the memory->size->examples tiers and enforces anti-drift rules:
  1. Every example's family_ref resolves to a curated.yml model entry
     (models.yml must NOT become a second source of truth).
  2. Tier structure matches the guides:
       - vram    <-> guides/choosing-models.md VRAM table
       - mac_ram <-> guides/choosing-models.md Mac table
       - cpu_ram <-> guides/cpu-only.md table
     The three groups exist because a CPU-only machine has far less memory
     bandwidth than an Apple Silicon Mac with the same RAM.
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MODELS = yaml.safe_load((REPO / "data" / "models.yml").read_text())
CURATED = yaml.safe_load((REPO / "data" / "curated.yml").read_text())
CHOOSING = (REPO / "guides" / "choosing-models.md").read_text()
CPU_ONLY = (REPO / "guides" / "cpu-only.md").read_text()

MODEL_CATEGORIES = {"models_general", "models_coding"}
VALID_BASIS = {"vram", "mac_ram", "cpu_ram"}


def _catalog():
    return {c["id"]: c for c in MODELS["catalog"]}


def _curated_model_names():
    return {
        e["name"]
        for e in CURATED["entries"]
        if e.get("category") in MODEL_CATEGORIES
    }


def _nums(text):
    """Integer tokens in a string, e.g. '30B-A3B MoE' -> {30, 3}."""
    return {int(n) for n in re.findall(r"\d+", text)}


def _tiers(basis):
    return [t for t in MODELS["tiers"] if t["basis"] == basis]


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
        assert t["basis"] in VALID_BASIS, t
        assert t["id"] not in seen, f"duplicate tier id {t['id']}"
        seen.add(t["id"])


def test_all_three_basis_groups_present():
    present = {t["basis"] for t in MODELS["tiers"]}
    assert present == VALID_BASIS, f"expected {VALID_BASIS}, got {present}"


def test_catalog_wellformed():
    for c in MODELS["catalog"]:
        for f in ("id", "name", "family_ref", "ollama", "why"):
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


# ── cpu tiers must carry honest expectation copy (Codex fix #2) ───────────

def test_cpu_tiers_set_honest_expectations():
    for t in _tiers("cpu_ram"):
        exp = t["expectations"].lower()
        assert any(w in exp for w in ("slower", "patient", "crawl", "modest", "cpu")), (
            f"cpu tier {t['id']} expectation copy doesn't set an honest CPU pace: {exp!r}"
        )


# ── drift check #1: models.yml <-> curated.yml ───────────────────────────

def test_every_catalog_family_resolves_to_curated():
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


# ── drift check #2: models.yml <-> the guides ────────────────────────────

def _table_rows(text, header_contains):
    """Data rows of the first markdown table whose header contains the marker."""
    rows, in_table = [], False
    for line in text.splitlines():
        if header_contains in line and line.strip().startswith("|"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            if set(line.strip()) <= set("|-: "):
                continue
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def _guide_by_mem(rows, size_col):
    out = {}
    for r in rows:
        nums = _nums(r[0])
        if nums:
            out[min(nums)] = _nums(r[size_col])
    return out


def test_vram_tiers_match_choosing_guide():
    rows = _table_rows(CHOOSING, "Model size that fits well")
    assert rows, "could not locate the VRAM size table in choosing-models.md"
    guide = _guide_by_mem(rows, 1)
    yaml_vram = {min(_nums(t["memory"])): _nums(t["size_class"]) for t in _tiers("vram")}
    assert set(yaml_vram) == set(guide), (
        f"VRAM tiers differ. yaml={sorted(yaml_vram)} guide={sorted(guide)}"
    )
    for mem, sizes in guide.items():
        # Exact match: the YAML must not offer larger/extra sizes than the guide
        # promises for a given VRAM tier (over-promise guard), nor fewer (drift guard).
        assert yaml_vram[mem] == sizes, (
            f"{mem}GB VRAM size drifted — yaml must match the guide exactly: "
            f"yaml={sorted(yaml_vram[mem])} guide={sorted(sizes)}"
        )


def test_mac_tiers_match_mac_table():
    rows = _table_rows(CHOOSING, "Comfortable class")
    assert rows, "could not locate the Mac RAM table in choosing-models.md"
    guide = _guide_by_mem(rows, 2)  # comfortable class column
    yaml_mac = {min(_nums(t["memory"])): _nums(t["size_class"]) for t in _tiers("mac_ram")}
    assert set(yaml_mac) == set(guide), (
        f"Mac tiers differ. yaml={sorted(yaml_mac)} guide={sorted(guide)}"
    )
    for mem, sizes in guide.items():
        # Exact match: same over-promise + drift guard as the VRAM table.
        assert yaml_mac[mem] == sizes, (
            f"{mem}GB Mac size drifted — yaml must match the guide exactly: "
            f"yaml={sorted(yaml_mac[mem])} guide={sorted(sizes)}"
        )


def test_cpu_tiers_match_cpu_only_guide():
    """cpu_ram tiers are grounded in cpu-only.md's own model table — the models
    the guide tells a CPU beginner to run must be the models the chooser offers."""
    rows = _table_rows(CPU_ONLY, "First model to run")
    assert rows, "could not locate the model table in cpu-only.md"
    # RAM -> set of model tags the guide recommends (from `backtick` spans)
    guide = {}
    for r in rows:
        nums = _nums(r[0])
        if nums:
            guide[min(nums)] = set(re.findall(r"`([^`]+)`", r[1]))
    assert guide, "no model tags parsed from cpu-only.md table"

    catalog = _catalog()
    cpu_by_mem = {}
    for t in _tiers("cpu_ram"):
        mem = min(_nums(t["memory"]))
        cpu_by_mem[mem] = {catalog[ex]["ollama"] for ex in t["examples"]}

    # every RAM level the guide documents must exist in the yaml and offer the
    # guide's recommended model(s)
    for mem, guide_tags in guide.items():
        assert mem in cpu_by_mem, f"cpu_ram has no {mem}GB tier (guide documents it)"
        assert guide_tags <= cpu_by_mem[mem], (
            f"{mem}GB CPU tier drifted from cpu-only.md: guide wants {guide_tags}, "
            f"yaml offers {cpu_by_mem[mem]}"
        )


def test_cpu_moe_placement_policy():
    """Policy lock for the qwen3:30b-a3b MoE on the CPU path.

    The MoE must not be offered below the 32 GB CPU tier. Concretely:
      - 32 GB CPU tier offers BOTH qwen3:8b (conservative first pick) AND the
        30B-A3B MoE (optional step up);
      - 8 GB and 16 GB CPU tiers must NOT offer the MoE;
      - 64 GB+ retains it (the ratified cpu4 MoE tier).
    Targeted by design — it inspects the chooser data (tier examples), not guide
    prose, so it stays robust while still catching a mis-tiered MoE.
    """
    catalog = _catalog()
    tags_by_mem = {}
    for t in _tiers("cpu_ram"):
        tags_by_mem[min(_nums(t["memory"]))] = {
            catalog[ex]["ollama"] for ex in t["examples"]
        }

    moe = "qwen3:30b-a3b"
    assert {"qwen3:8b", moe} <= tags_by_mem.get(32, set()), (
        f"32 GB CPU tier must offer both qwen3:8b and {moe}; got {tags_by_mem.get(32)}"
    )
    for mem in (8, 16):
        assert moe not in tags_by_mem.get(mem, set()), (
            f"{mem} GB CPU tier must NOT offer {moe} (below the 32 GB MoE floor): "
            f"{tags_by_mem.get(mem)}"
        )
    assert moe in tags_by_mem.get(64, set()), (
        f"64 GB+ CPU tier should retain {moe} (ratified cpu4 MoE tier); "
        f"got {tags_by_mem.get(64)}"
    )

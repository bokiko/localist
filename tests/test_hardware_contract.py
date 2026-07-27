"""PR-1 data contract: data/hardware.yml.

Validates the hardware-chooser taxonomy and asserts its flow matches the prose
in guides/start-here.md (the human source of truth). The website's chooser will
read this file; these tests keep it faithful to the guide.
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
HARDWARE = yaml.safe_load((REPO / "data" / "hardware.yml").read_text())
START_HERE = (REPO / "guides" / "start-here.md").read_text()

VALID_MEMORY_BASIS = {"vram", "ram"}


def _ids(items):
    return [x["id"] for x in items]


def test_top_level_shape():
    assert HARDWARE.get("version") == 1
    for key in ("platforms", "accelerators", "memory_tiers", "mistakes", "helpers"):
        assert key in HARDWARE, f"hardware.yml missing '{key}'"


def test_platforms_wellformed():
    platforms = HARDWARE["platforms"]
    ids = _ids(platforms)
    # the five the product spec fixed
    assert set(ids) == {"windows", "mac", "linux", "mini_pc", "not_sure"}
    for p in platforms:
        assert p.get("label")
        # each platform must either ask for an accelerator, imply one, or route to helper
        assert (
            p.get("asks_accelerator")
            or p.get("implies_accelerator")
            or p.get("routes_to") == "helper"
        ), f"platform '{p['id']}' has no accelerator resolution"


def test_accelerators_wellformed_and_basis_valid():
    accels = HARDWARE["accelerators"]
    ids = _ids(accels)
    assert {"nvidia", "amd", "apple_silicon", "cpu_only", "not_sure"} == set(ids)
    for a in accels:
        if a.get("routes_to") == "helper":
            continue
        assert a["memory_basis"] in VALID_MEMORY_BASIS, a
        # memory_basis must name an actual tier group
        assert a["memory_basis"] in HARDWARE["memory_tiers"], a
        assert a.get("guide"), f"accelerator '{a['id']}' missing guide slug"


def test_accelerator_guides_exist_as_files():
    for a in HARDWARE["accelerators"]:
        slug = a.get("guide")
        if not slug:
            continue
        assert (REPO / "guides" / f"{slug}.md").exists(), (
            f"accelerator '{a['id']}' points at missing guide {slug}.md"
        )


def test_memory_tier_groups_reference_model_tiers():
    tiers = HARDWARE["memory_tiers"]
    assert set(tiers.keys()) == {"vram", "ram"}
    for group, buckets in tiers.items():
        assert buckets, f"empty memory tier group {group}"
        for b in buckets:
            assert b.get("id") and b.get("label") and b.get("model_tier"), b


# ── fidelity to start-here.md ────────────────────────────────────────────

def test_mac_implies_apple_silicon_like_the_guide():
    mac = next(p for p in HARDWARE["platforms"] if p["id"] == "mac")
    assert mac.get("implies_accelerator") == "apple_silicon"
    # the guide routes Intel Macs to cpu-only
    assert mac.get("intel_fallback") == "cpu_only"
    assert "Apple M1" in START_HERE and "Intel" in START_HERE


def test_gpu_paths_use_vram_cpu_and_mac_use_ram():
    basis = {a["id"]: a.get("memory_basis") for a in HARDWARE["accelerators"]}
    assert basis["nvidia"] == "vram"
    assert basis["amd"] == "vram"
    assert basis["apple_silicon"] == "ram"
    assert basis["cpu_only"] == "ram"
    # the guide states this basis rule explicitly
    assert "VRAM" in START_HERE and "RAM" in START_HERE


def test_every_accelerator_guide_is_linked_from_start_here():
    for a in HARDWARE["accelerators"]:
        slug = a.get("guide")
        if not slug:
            continue
        assert f"{slug}.md" in START_HERE, (
            f"{slug}.md is not linked from start-here.md — flow drift"
        )


def test_helpers_cover_the_not_sure_branches():
    helpers = HARDWARE["helpers"]
    # a not-sure GPU/platform user must never dead-end
    assert any("gpu" in k for k in helpers), "no GPU-detection helper"
    assert any("mac" in k for k in helpers), "no Mac-chip helper"
    # helper values are non-empty instructions
    for k, v in helpers.items():
        assert isinstance(v, str) and v.strip(), f"empty helper {k}"

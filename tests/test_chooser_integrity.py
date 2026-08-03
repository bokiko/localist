"""PR-1 data contract: cross-file integrity between hardware.yml and models.yml.

The chooser resolves platform -> accelerator -> memory bucket -> model_tier ->
models.yml tier. Nothing else tests that this wiring actually connects, so
renaming a tier id in one file could silently break the chooser while the
per-file schema tests stay green. These tests are the regression lock.
"""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
HARDWARE = yaml.safe_load((REPO / "data" / "hardware.yml").read_text())
MODELS = yaml.safe_load((REPO / "data" / "models.yml").read_text())


def _model_tiers_by_id():
    return {t["id"]: t for t in MODELS["tiers"]}


def _catalog():
    return {c["id"]: c for c in MODELS["catalog"]}


# ── the regression lock: every hardware bucket resolves, with matching basis ──

def test_every_hardware_bucket_resolves_to_a_model_tier_with_matching_basis():
    model_tiers = _model_tiers_by_id()
    for group, buckets in HARDWARE["memory_tiers"].items():
        for bucket in buckets:
            tier_id = bucket["model_tier"]
            # 1. the referenced model tier must exist
            assert tier_id in model_tiers, (
                f"hardware.yml {group}/{bucket['id']} points at model_tier "
                f"'{tier_id}' which does not exist in models.yml"
            )
            # 2. the resolved tier's basis must equal the hardware group name
            resolved_basis = model_tiers[tier_id]["basis"]
            assert resolved_basis == group, (
                f"basis mismatch: hardware group '{group}' bucket "
                f"'{bucket['id']}' -> model tier '{tier_id}' has basis "
                f"'{resolved_basis}' (expected '{group}')"
            )


def test_accelerator_memory_basis_matches_a_hardware_tier_group():
    groups = set(HARDWARE["memory_tiers"].keys())
    for a in HARDWARE["accelerators"]:
        if a.get("routes_to") == "helper":
            continue
        assert a["memory_basis"] in groups, (
            f"accelerator '{a['id']}' memory_basis '{a['memory_basis']}' is not a "
            f"memory_tiers group {groups}"
        )


# ── encoded beginner path: Windows -> integrated graphics -> 16 GB RAM ──────

def _resolve(accelerator_id, bucket_id):
    """Resolve the chooser bundle the way the site will, from data alone."""
    accel = next(a for a in HARDWARE["accelerators"] if a["id"] == accelerator_id)
    basis = accel["memory_basis"]
    bucket = next(b for b in HARDWARE["memory_tiers"][basis] if b["id"] == bucket_id)
    tier = _model_tiers_by_id()[bucket["model_tier"]]
    catalog = _catalog()
    example_tags = [catalog[ex]["ollama"] for ex in tier["examples"]]
    return {
        "guide": accel["guide"],
        "model_tier": tier["id"],
        "size_class": tier["size_class"],
        "example_tags": example_tags,
        "expectations": tier["expectations"],
        "mistakes": HARDWARE["mistakes"].get(accel["id"], []),
    }


def test_windows_integrated_16gb_beginner_bundle():
    """The demonstrated path, locked as a test: a 16 GB integrated-graphics user
    must be routed to the CPU guide and a 3B–4B model — NOT the Mac-calibrated 8B."""
    bundle = _resolve("integrated", "16gb")
    assert bundle["guide"] == "cpu-only"
    assert bundle["model_tier"] == "cpu2"
    assert "4B" in bundle["size_class"]           # 3B–4B class
    assert "qwen3:4b" in bundle["example_tags"]
    assert bundle["expectations"].strip()          # non-empty honest copy
    assert bundle["mistakes"]                        # non-empty pitfalls
    # regression guard against the original bug: must not offer the 8B tier's model
    assert "qwen3:8b" not in bundle["example_tags"], (
        "16 GB CPU/integrated path is offering an 8B model — the over-promise bug"
    )

"""Discovery policy tests — every fixture is a REAL discovery from the
2026-07-16..19 live feed, labeled in the Phase 0 pass. If the policy ever
regresses on these, it regresses on reality."""

import datetime
from pathlib import Path

import httpx
import pytest

from sources.github_discoveries import (
    fetch_discoveries,
    load_discovery_policy,
    policy_verdict,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY = load_discovery_policy(REPO_ROOT / "data" / "discovery.yml")
DATE = datetime.date(2026, 7, 19)


def item(name, desc, stars=100):
    return {
        "full_name": name,
        "html_url": f"https://github.com/{name}",
        "description": desc,
        "stargazers_count": stars,
        "created_at": "2026-07-15T00:00:00Z",
        "topics": ["local-ai"],  # always present via topic search — must NOT
        # count toward relevance (else every rule passes vacuously)
    }


# ── the eleven real Phase 0 examples ─────────────────────────────────

DROPS = [
    item(
        "thClaws/thClaws",
        "Open-source AI agent harness in native Rust — GUI, CLI, headless, and "
        "webapp from one binary. Multi-provider, MCP, skills, plugins, agent teams.",
    ),
    item(
        "kennss/SiliconScope",
        "Sudoless Apple Silicon system monitor (native SwiftUI GUI) with ANE / "
        "Media Engine / memory-bandwidth tracking",
    ),
    item("r14dd/patent", "A prior-art search for your code ideas — has this dev tool already been shipped?"),
    item(
        "techjarves/Uncensored-Local-Studio",
        "Uncensored local AI studio for Windows, Linux, and macOS. Zero-setup GUI "
        "for Image Generation, GGUF LLMs, Text to Speech & Speech to Text",
    ),
]

KEEPS = [
    item("Gitlawb/zero", "The coding agent that answers to you, your model, your machine, your rules."),
    item(
        "AtomicBot-ai/atomic-agent",
        "Local First Ai Agent. Optimized for Local Ai models. Long context window. "
        "Proper tools callings. Runs privately on your device.",
    ),
    item("deepanwadhwa/samosa-chat", "Run Qwen3.6-35B-A3B locally on a 16 GB RAM machine"),
    item(
        "giannisanni/pulsar",
        "SSD-streaming inference engine for giant MoE models (Rust + CUDA). "
        "Zero-config multi-GPU.",
    ),
    item(
        "bbarit/bbarit-agent-oss",
        "Open-source AI coding agent for your terminal — one Rust binary, 15+ LLM "
        "providers, 1,000+ models. A self-hostable Claude Code / Codex CLI alternative (MIT).",
    ),
    item(
        "youssofal/MTPLX",
        "2.24x decode TPS increase On Qwen 3.6 27B @ temp 0.6 | Native MTP "
        "Speculative Decoding On Apple Silicon With No External Drafter.",
    ),
    item("zeraix/zeraix", "Open-source local AI workspace — advancing on-device inference."),
]


@pytest.mark.parametrize("fixture", DROPS, ids=lambda f: f["full_name"])
def test_phase0_drops_are_dropped(fixture):
    passes, reason = policy_verdict(fixture, POLICY)
    assert passes is False
    assert reason  # every drop carries a loggable reason


@pytest.mark.parametrize("fixture", KEEPS, ids=lambda f: f["full_name"])
def test_phase0_keeps_are_kept(fixture):
    passes, reason = policy_verdict(fixture, POLICY)
    assert passes is True


def test_editorial_hold_reason_is_specific():
    _, reason = policy_verdict(DROPS[3], POLICY)  # Uncensored-Local-Studio
    assert "editorial" in reason.lower()


def test_agent_without_local_signal_reason():
    _, reason = policy_verdict(DROPS[0], POLICY)  # thClaws
    assert "agent" in reason.lower()


# ── manual overrides ─────────────────────────────────────────────────


def test_allowlist_beats_all_rules():
    policy = dict(POLICY)
    policy["allowlist_repos"] = ["r14dd/patent"]
    passes, _ = policy_verdict(DROPS[2], policy)
    assert passes is True


def test_blocklist_beats_all_rules():
    policy = dict(POLICY)
    policy["blocklist_repos"] = ["deepanwadhwa/samosa-chat"]
    passes, reason = policy_verdict(KEEPS[2], policy)
    assert passes is False
    assert "blocklist" in reason.lower()


# ── integration: fetch applies policy and logs drops ─────────────────


def test_fetch_filters_and_logs_drops(capsys):
    all_items = DROPS + KEEPS

    def handler(request):
        return httpx.Response(200, json={"items": all_items})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    out = fetch_discoveries(client, DATE, set(), set(), policy=POLICY, cap=20)
    names = {d["name"] for d in out}
    assert "thClaws/thClaws" not in names
    assert "kennss/SiliconScope" not in names
    assert "r14dd/patent" not in names
    assert "techjarves/Uncensored-Local-Studio" not in names
    assert {k["full_name"] for k in KEEPS} == names
    err = capsys.readouterr().err
    assert "thClaws/thClaws" in err  # dropped repos are logged with a reason


def test_fetch_without_policy_is_unfiltered():
    def handler(request):
        return httpx.Response(200, json={"items": DROPS})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    out = fetch_discoveries(client, DATE, set(), set(), cap=20)
    assert len(out) == 4  # backward-compatible: no policy → no filtering

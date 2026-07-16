# Localist

> **The local AI list that updates itself.** Run AI on your own machine — start here, check back daily.

![Last updated](https://img.shields.io/github/last-commit/bokiko/localist?label=updated)
![Stars](https://img.shields.io/github/stars/bokiko/localist)
![Code: MIT](https://img.shields.io/badge/code-MIT-green)
![Content: CC--BY--4.0](https://img.shields.io/badge/content-CC--BY--4.0-blue)

Most local-AI lists are snapshots that quietly go stale. Localist is different:
a daily GitHub Action refreshes the **What's New** section below with new and active
projects and fresh tool releases — so what you read here is what's true *today*.

---

## 🔥 What's New

<!-- NEWS:START -->
*Updated 2026-07-16*

**🆕 New & active projects**
- [thClaws/thClaws](https://github.com/thClaws/thClaws) — Open-source AI agent harness in native Rust — GUI, CLI, headless, and webapp from one binary. Multi-provider, MCP, skills, plugins, agent teams. · ⭐ 1158
- [Gitlawb/zero](https://github.com/Gitlawb/zero) — The coding agent that answers to you, your model, your machine, your rules. · ⭐ 1089
- [kennss/SiliconScope](https://github.com/kennss/SiliconScope) — Sudoless Apple Silicon system monitor (native SwiftUI GUI) with ANE / Media Engine / memory-bandwidth tracking · ⭐ 750
- [AtomicBot-ai/atomic-agent](https://github.com/AtomicBot-ai/atomic-agent) — Local First Ai Agent. Optimized for Local Ai models. Long context window. Proper tools callings. Runs privately on your device. · ⭐ 723
- [deepanwadhwa/samosa-chat](https://github.com/deepanwadhwa/samosa-chat) — Run Qwen3.6-35B-A3B locally on a 16 GB RAM machine · ⭐ 32

**📦 Tool releases**
- [Ollama v0.32.0](https://github.com/ollama/ollama/releases/tag/v0.32.0) — What's Changed New interactive agent experience: running `ollama` now launches an agent to help you code and delegate work
- [vLLM v0.25.1](https://github.com/vllm-project/vllm/releases/tag/v0.25.1) — vLLM v0.25.1 Highlights
- [vLLM v0.25.0](https://github.com/vllm-project/vllm/releases/tag/v0.25.0) — vLLM v0.25.0 Release Notes Highlights
- [KoboldCpp v1.117.1](https://github.com/LostRuins/koboldcpp/releases/tag/v1.117.1) — koboldcpp-1.117.1 Fixed terminal output sometimes not showing thinking traces
- [ComfyUI v0.28.0](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.28.0) — What's Changed Add AGENTS.md by @comfyanonymous in https://github.com/Comfy-Org/ComfyUI/pull/14696
- [LM Studio 0.4.19](https://lmstudio.ai/changelog/lmstudio-v0.4.19)
<!-- NEWS:END -->

[Full news archive →](news/)

---

## 🚀 Start Here — pick your hardware

Don't read everything. Find your row, follow one guide, and you'll be chatting with a
local model in under 15 minutes.

| I have… | Your guide |
|---|---|
| **An NVIDIA GPU** (any GeForce RTX) | [NVIDIA GPU path](guides/nvidia-gpu.md) |
| **A Mac with Apple Silicon** (M1–M4) | [Mac path](guides/mac-apple-silicon.md) |
| **An AMD GPU** (Radeon RX) | [AMD GPU path](guides/amd-gpu.md) |
| **Just a laptop / no GPU** | [CPU-only path](guides/cpu-only.md) |
| **No idea what I have** | [Start here](guides/start-here.md) |

---

## 🧰 The Essentials

One opinionated pick per category. Alternatives are inside each entry — but if you're
new, just take the pick and move on.

| Category | Our pick | Why this one |
|---|---|---|
| **Model runner** | [Ollama](https://github.com/ollama/ollama) | One command to install, one to run a model. The de-facto beginner standard. |
| **Desktop app** | [LM Studio](https://lmstudio.ai) | Point-and-click everything: browse, download, and chat with models. No terminal needed. |
| **Web UI** | [Open WebUI](https://github.com/open-webui/open-webui) | ChatGPT-style interface on top of Ollama. Multi-user, RAG, voice. |
| **Chat models** | Qwen3 / Gemma 3 / Phi-4 Mini | Best quality-per-GB right now. Which size fits you → [choosing models](guides/choosing-models.md). |
| **Coding agent** | [OpenCode](https://github.com/anomalyco/opencode) | Most popular open-source coding agent; points at your local models. |
| **Engine (advanced)** | [llama.cpp](https://github.com/ggml-org/llama.cpp) | The engine most tools are built on. Go direct when you outgrow the wrappers. |
| **Image generation** | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Node-based, runs every major open image model. Steeper curve, unmatched power. |
| **Chat with your docs** | [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) | Point it at a folder and a local model — done. |
| **Speech-to-text** | [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Fast local transcription on any hardware. |

The full curated set (30 entries with licenses, hardware fit, and honest caveats)
lives in [`data/curated.yml`](data/curated.yml).

---

## 📚 New to all of this?

The [glossary](guides/glossary.md) explains every term you'll bump into —
GGUF, quantization, context window, VRAM, tokens/sec — in plain words.
And [choosing models](guides/choosing-models.md) answers the #1 question:
*which model size actually fits my machine?*

## 🤝 Contributing

Found a great tool? Spotted a dead project? Open an issue —
[suggest a tool](../../issues/new?template=suggest-tool.yml) ·
[report a stale entry](../../issues/new?template=report-stale.yml).
See [CONTRIBUTING.md](CONTRIBUTING.md) for the ground rules.

## ⭐ Why this list is different

1. **It updates itself, daily.** A pipeline (not vibes) refreshes the What's New block every morning.
2. **It's opinionated.** One recommended pick per category, not 40 tools to compare.
3. **It's hardware-first.** You start from what you own, not from an alphabet of projects.
4. **It removes dead things.** Stale entries get flagged and dropped, not hoarded.

## 📄 License

- Code and scripts: [MIT](LICENSE)
- Guides and written content: [CC-BY-4.0](LICENSE-CONTENT)

<p align="center">
  <img src="assets/logo.png" alt="Localist — local AI, made simple" width="520">
</p>

# Localist

> **Run AI on your own machine.** Pick your hardware, install one tool, chat with a model that fits — this page gets a beginner there in about 15 minutes.

![Last updated](https://img.shields.io/github/last-commit/bokiko/localist?label=updated)
![Stars](https://img.shields.io/github/stars/bokiko/localist)
![Code: MIT](https://img.shields.io/badge/code-MIT-green)
![Content: CC--BY--4.0](https://img.shields.io/badge/content-CC--BY--4.0-blue)

<p align="center">
  <a href="https://medium.com/p/dadded1dda24">Backstory</a> ·
  <a href="https://x.com/bokiko">Follow updates on X</a>
</p>

Localist is a beginner-first guide, not another giant tool list. You start from the
machine you already own, follow one guide, and skip the other 50 options. And it
doesn't rot: a pipeline — not vibes — refreshes the
[Fresh updates](#-fresh-updates) section every morning, and we review and prune
stale recommendations instead of hoarding them.

**Jump to:** [Start here](#-start-here--pick-your-hardware) ·
[The essentials](#-the-essentials) · [Fresh updates](#-fresh-updates) ·
[Glossary](guides/glossary.md) · [Contributing](#-contributing)

**Not sure what hardware you have?** → [Work it out in two questions](guides/start-here.md)
· **Something not working?** → [Troubleshooting](guides/troubleshooting.md)

---

## 🚀 Start here — pick your hardware

Don't read everything. Find your row, follow one guide, and you'll be chatting with a
local model in under 15 minutes.

<p align="center">
  <img src="assets/steps.jpg" alt="Four steps: identify your hardware, install one tool, download one model that fits, start chatting" width="680">
</p>

| I have… | Your guide |
|---|---|
| **An NVIDIA GPU** (any GeForce RTX) | [NVIDIA GPU path](guides/nvidia-gpu.md) |
| **A Mac with Apple Silicon** (M-series) | [Mac path](guides/mac-apple-silicon.md) |
| **An AMD GPU** (Radeon RX) | [AMD GPU path](guides/amd-gpu.md) |
| **Just a laptop / no GPU** | [CPU-only path](guides/cpu-only.md) |
| **A mini PC or home server** | [CPU-only path](guides/cpu-only.md) — or the [NVIDIA path](guides/nvidia-gpu.md) if it has a GPU |
| **No idea what I have** | [Start here](guides/start-here.md) |

Everything here can run locally; many paths work offline after setup, and your
prompts stay on your machine unless you connect a cloud service.

**Stuck partway?** [Troubleshooting](guides/troubleshooting.md) covers the handful of
things that actually go wrong — including *"where do I type this command?"*, how to
stop the chat, and how to start it again tomorrow.

---

## 🧰 The essentials

One opinionated pick per category. Alternatives are inside each entry — but if
you're new, just take the pick and move on.

**Which tool first?** Want clicks? Start with LM Studio. Comfortable with one
command? Start with Ollama. You do not need both.

| Category | Our pick | Why this one |
|---|---|---|
| **Model runner** | [Ollama](https://github.com/ollama/ollama) | One command to install, one to run a model. The de-facto beginner standard. |
| **Desktop app** | [LM Studio](https://lmstudio.ai) | Point-and-click everything: browse, download, and chat with models. No terminal needed. |
| **Web UI** | [Open WebUI](https://github.com/open-webui/open-webui) | ChatGPT-style interface on top of Ollama. Multi-user, chat with your documents, voice. |
| **Chat models** | [Qwen3 family](https://ollama.com/library/qwen3) | Strong at every size, tiny to huge. Which size fits you → [choosing models](guides/choosing-models.md). |
| **Coding models** | [Qwen Coder](https://ollama.com/library/qwen3-coder) | Same idea, meaningfully better at code. Pairs with the coding agent below. |
| **Coding agent** | [OpenCode](https://github.com/anomalyco/opencode) | Most popular open-source coding agent; points at your local models. |
| **Image generation** | [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Node-based, runs every major open image model. Steeper curve, unmatched power. |
| **Chat with your docs** | [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) | Point it at a folder and a local model — done. |
| **Speech-to-text** | [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Fast local transcription on any hardware. |
| **Text-to-speech** | [Piper](https://github.com/OHF-Voice/piper1-gpl) | Fast, natural offline voices — runs even on a Raspberry Pi. |

When you outgrow beginner tools, [llama.cpp](https://github.com/ggml-org/llama.cpp)
is the engine worth learning — it's what most of the tools above are built on.

The full curated set (with licenses, hardware fit, and honest caveats) lives in
[`data/curated.yml`](data/curated.yml) — it's the single source of truth these
picks come from.

---

## 🔥 Fresh updates

New projects and tool releases from the past week, refreshed daily by the pipeline.
*Pipeline-surfaced projects are not curated recommendations. Start with the
Essentials table above if you want the trusted beginner picks.*

<!-- NEWS:START -->
*Updated 2026-08-29*

**🆕 New & active projects**
- [ARahim3/mlx-dspark](https://github.com/ARahim3/mlx-dspark) — Up to 4× faster LLM decoding on Apple Silicon, lossless. Native MLX port of DeepSeek's DSpark & z-lab's DFlash speculative decoding — Gemma-4, Qwen3.8, Muse-Glimmer, Nemotron, LFM2.5, Ornith-1.0, · ⭐ 584
- [Vincent-Xi08/IntentRoute-AI](https://github.com/Vincent-Xi08/IntentRoute-AI) — Open-source AI-assisted per-application routing for Windows with OpenAI/Ollama drafts and a sing-box TUN data plane. · ⭐ 59
- [Lucas-Xi/IntentRoute-AI](https://github.com/Lucas-Xi/IntentRoute-AI) — Open-source AI-assisted per-application routing for Windows with OpenAI/Ollama drafts and a sing-box TUN data plane. · ⭐ 37

**📦 Tool releases**
- [llama.cpp v0.3.0](https://github.com/ggml-org/llama.cpp/releases/tag/v0.3.0) — Overview llama.cpp 0.3.0 introduces the dots3-note multimodal model (with a new DSA-ISWA KV cache), MTP support for GLM-4.5-Air, and tensor-split (`-sm tensor`) plus multi-sequence rollback fixes for
- [Ollama v0.33.0](https://github.com/ollama/ollama/releases/tag/v0.33.0) — Claude Desktop Developers can now easily configure Claude Desktop to seamlessly work with Ollama as a third-party gateway provider.
- [Open WebUI v0.11.1](https://github.com/open-webui/open-webui/releases/tag/v0.11.1) — Added 🚦 **Human in the loop tool approval.** Where an administrator has turned it on, you can switch a conversation from letting tools run freely to being asked first, so a model that wants to use a
- [ComfyUI v0.34.0](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.34.0) — Fix minimax music not working on non dynamic vram. Add MiniMaxH3AddGuide for anchoring image and audio guides at any frame
- [Ollama v0.33.1](https://github.com/ollama/ollama/releases/tag/v0.33.1) — MLX: Qwen3.8 Flash Next support cmake: make external compat patches idempotent
- [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) — This release features 584 commits from 270 contributors (76 new)! **Kimi-K3 performance push**: a major optimization effort for Kimi-K3 across the stack — Decode Context Parallel (DCP) support
- [LM Studio 1.1.0](https://lmstudio.ai/changelog/bionic-v1.1.0)
- [Ollama v0.33.2](https://github.com/ollama/ollama/releases/tag/v0.33.2) — Ollama's app now follows the system appearance again, restoring dark mode support Fixed the macOS app to properly hand off to an already-running instance instead of starting a second one
- [KoboldCpp v1.120](https://github.com/LostRuins/koboldcpp/releases/tag/v1.120) — Minor fix to assistant gen prefills being triggered incorrectly Fixed a bug where failsafe mode was incorrectly selected
<!-- NEWS:END -->

[Full news archive →](news/)

---

## 📚 New to all of this?

Don't know what hardware you have? [Start here](guides/start-here.md) works it out in
two questions, and tells you what a local model will and won't do well before you
spend time on it.

The [glossary](guides/glossary.md) explains every term you'll bump into —
GGUF, quantization, weights, context window, VRAM, tokens/sec — in plain words.
And [choosing models](guides/choosing-models.md) answers the #1 question:
*which model size actually fits my machine?*

When something doesn't work, [troubleshooting](guides/troubleshooting.md) is organised
by what you see on screen — not by what went wrong underneath.

## 🤝 Contributing

Found a great tool? Spotted a dead project? Open an issue —
[suggest a tool](https://github.com/bokiko/localist/issues/new?template=suggest-tool.yml) ·
[report a stale entry](https://github.com/bokiko/localist/issues/new?template=report-stale.yml).
If a link, download, or command looks unsafe or compromised, report it privately
through [SECURITY.md](SECURITY.md) instead of a public issue.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the ground rules.

## 📄 License

- Code and scripts: [MIT](LICENSE)
- Guides and written content: [CC-BY-4.0](LICENSE-CONTENT)

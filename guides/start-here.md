# Start Here — figure out what you have

You want to run AI on your own machine but don't know where to begin.
Answer two questions and this page routes you to the right guide.

## Question 1: What kind of computer do you have?

### "A Mac"
Click the Apple menu → **About This Mac**. If the chip says **Apple M1, M2, M3, or M4**
(any variant — Pro, Max, Ultra), you're in great shape:

→ **[Mac (Apple Silicon) guide](mac-apple-silicon.md)**

If it says **Intel**, treat it as a CPU-only machine:

→ **[CPU-only guide](cpu-only.md)**

### "A Windows PC or Linux machine"
You need to know your graphics card (GPU):

- **Windows:** press `Ctrl+Shift+Esc` → Performance tab → look for **GPU**
- **Linux:** run `lspci | grep -i vga` in a terminal

| Your GPU says… | Go to |
|---|---|
| NVIDIA / GeForce RTX / GTX | [NVIDIA guide](nvidia-gpu.md) |
| AMD / Radeon RX | [AMD guide](amd-gpu.md) |
| Intel Arc / Intel Iris / "integrated" | [CPU-only guide](cpu-only.md) *(for now — Vulkan support for Intel GPUs is improving, so this routing may change)* |
| No GPU listed | [CPU-only guide](cpu-only.md) |

## Question 2: How much memory does it have?

This decides how big a model you can run. Rough expectations:

| Memory | What you can expect |
|---|---|
| 8 GB | Small models (3–4B). Fine for chat, summaries, quick questions. |
| 16 GB | Mid-size models (7–14B). Genuinely useful daily-driver territory. |
| 24–32 GB | Large models (14–32B). Quality that rivals cloud chatbots for many tasks. |
| 64 GB+ | The big leagues (70B+). You probably didn't need this page. |

**Note for GPU owners:** what matters is the GPU's own memory (**VRAM**), not system RAM.
Your hardware guide explains how to check it. For the full size-by-memory breakdown,
see [choosing models](choosing-models.md).

## What "running AI locally" actually gets you

- **Privacy** — your conversations never leave your machine
- **Free** — no subscription, no API bills, no rate limits
- **Offline** — works on a plane, works when the internet is down
- **Control** — pick your model, tune it, swap it, no one can take it away

The trade-off: local models are smaller than the biggest cloud models. For everyday
chat, writing help, coding assistance, and summarization, a good local model on
16 GB+ of memory feels remarkably close.

## Words you'll bump into

Model names look like `qwen3:8b-q4_K_M`. The [glossary](glossary.md) decodes all of it
in plain words. You don't need it to get started — your hardware guide gives exact
commands to copy-paste.

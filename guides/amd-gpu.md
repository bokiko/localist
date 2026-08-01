# AMD GPU Path — better than its reputation

You have a Radeon RX card. The old advice was "AMD and local AI don't mix" — that's
outdated. ROCm 7.x has significantly improved AMD support, and Ollama, LM Studio,
llama.cpp, and vLLM all run on Radeon — though exact compatibility depends on your
GPU model and OS, so check the
[AMD ROCm compatibility docs](https://rocm.docs.amd.com/) for your card. There's
also an even easier path (Vulkan) that skips ROCm entirely.

**Honest summary:** NVIDIA is still the smoothest ride. AMD now works well, with
roughly two setup styles:

| Path | Effort | Performance |
|---|---|---|
| **Vulkan** (via LM Studio) | Almost zero | Close to ROCm for most use |
| **ROCm** (via Ollama/llama.cpp) | Moderate (best on Linux) | Full speed |

## Step 0: Check your card and VRAM

**Windows:** `Ctrl+Shift+Esc` → Performance → GPU, and read the
**Dedicated GPU memory** figure. If more than one GPU is listed, pick the one
named Radeon RX.

**Linux:** if you have ROCm installed, `rocm-smi --showmeminfo vram`. If you
don't, ask the driver directly — this works with no extra packages:

```bash
awk '{printf "%.1f GB VRAM  (%s)\n", $1/1073741824, FILENAME}' \
  /sys/class/drm/card*/device/mem_info_vram_total
```

Only AMD cards appear here, one line each.

- **Two lines?** Your CPU has built-in graphics as well as your Radeon. Take
  the **larger** number — built-in graphics reserve much less, usually well
  under 2 GB. A line reading `0.5 GB` is the built-in one, not a broken card.
  Then read the rules below for that larger number.
- **8 GB or more?** That's your Radeon. Use it in the table below.
- **Under 8 GB but 2 GB or more?** A real Radeon, just a small one — the 4 GB version of
  the RX 6500 XT lands here — or a generous built-in-graphics allocation. Either
  way it's under this table's 8 GB floor, so the models here are too big for it.
  [CPU-only](cpu-only.md) has the sizes that will actually run.
- **Under 2 GB?** That's your CPU's built-in graphics, not a separate card.
  [CPU-only](cpu-only.md) is your path.
- **An error instead of a number?** (`no matches found`, or `cannot open file`.)
  The `amdgpu` driver isn't loaded for your card. Check the
  [ROCm compatibility docs](https://rocm.docs.amd.com/) before going further —
  local AI won't use the GPU until that's sorted.

Two commands worth skipping: `lspci | grep -i vga` names your card but never
prints its VRAM, and `glxinfo` reports whichever GPU is currently driving your
display — on a laptop that's usually the built-in one, so it can hand you a
*larger* number than your Radeon actually has and send you to the wrong row.

| VRAM | Example cards | First model to run |
|---|---|---|
| 8 GB | — | `qwen3:4b` |
| 12 GB | — | `qwen3:8b` |
| 16 GB | RX 7800 XT, RX 9070 / 9070 XT | `qwen3:14b` |
| 20 GB | RX 7900 XT | `qwen3:14b` |
| 24 GB | RX 7900 XTX | `qwen3:32b` or `gemma3:27b` |

**Why 20 GB and 24 GB are separate rows:** `qwen3:32b` is 18.8 GiB of weights.
On a 24 GB card that is 78% — it fits with room for context. On a 20 GB card it
is 94%, which leaves nothing for the context window, so it either crawls on a
partial CPU offload or fails to load. `gemma3:27b` (16.2 GiB) is 81% of a 20 GB
card — technically loadable, but only with a short context.

RDNA4 cards (RX 9070, RX 9070 XT) are supported by ROCm — check the
[compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html)
for your exact model and distro before you plan around it.

## Easiest path: LM Studio with Vulkan (Windows & Linux)

1. Download [LM Studio](https://lmstudio.ai) (free)
2. In settings, the runtime should already show **Vulkan** — no drivers, no ROCm, nothing
3. Search a model from your tier, download, chat

Vulkan gives you most of the performance with none of the setup. Start here;
only bother with ROCm if you want to squeeze out the last bit of speed.

## Full-speed path: Ollama with ROCm (Linux recommended)

1. Install ROCm following [AMD's official guide](https://rocm.docs.amd.com/) for your distro
2. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   *(Prefer not to pipe scripts into your shell? Use the manual install steps on
   [ollama.com/download](https://ollama.com/download) instead — same result.)*
3. Run a model:
   ```bash
   ollama run qwen3:8b
   ```
   Ollama detects the GPU via ROCm automatically. Verify with `ollama ps`
   (should show 100% GPU) or watch `rocm-smi` during generation.

**Windows + ROCm** is supported but consistently a step behind Linux in driver
maturity. If you're on Windows, take the Vulkan path unless you have a reason not to.

## Known sharp edges

- **Older cards (RX 5000/6000 series):** ROCm support varies by exact model —
  check [AMD's compatibility matrix](https://rocm.docs.amd.com/). Vulkan usually
  still works even when ROCm doesn't.
- **Integrated Radeon graphics:** treat as [CPU-only](cpu-only.md).
- **Image generation (ComfyUI):** works on ROCm but with more friction than
  LLMs — expect occasional workarounds.

## Where to go next

- **ChatGPT-style interface:** [Open WebUI](https://github.com/open-webui/open-webui) on top of Ollama
- **Coding assistant:** [Aider](https://github.com/Aider-AI/aider) (terminal) or
  [OpenCode](https://github.com/anomalyco/opencode) pointed at your local API
- **Which model size fits your card:** [choosing models](choosing-models.md)
- **Stuck?** [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) — plenty of Radeon owners there

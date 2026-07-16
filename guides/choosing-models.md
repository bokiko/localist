# Choosing Models — what fits your machine

The single most common beginner question: *"which model can I actually run?"*
The answer is almost entirely about **memory** — your GPU's VRAM, or on a Mac,
your unified memory.

## The size table

Assumes standard Q4 quantization (the default when you download from Ollama or
LM Studio). "Parameters" is the `B` number in the model name.

| Your memory | Model size that fits well | Examples |
|---|---|---|
| **8 GB** (VRAM or RAM) | 1B–4B | Qwen3 4B, Phi-4 Mini, Gemma 3 4B, Llama 3.2 3B |
| **12 GB VRAM** | 7B–8B sweet spot | Qwen3 8B, Llama 3.1 8B |
| **16 GB VRAM** | 14B class | Qwen3 14B, Gemma 3 12B |
| **24 GB VRAM** | 30B/32B class | Qwen3 32B, Gemma 3 27B, Devstral Small |
| **48 GB+** (dual GPU / Mac / workstation) | 70B class | Llama 3.3 70B, R1-distill 70B |

**Rule of thumb:** the model's *download size* should be at most ~80% of your
available memory — the rest is needed for the context window and overhead.

## Apple Silicon: unified memory is shared

A "32 GB Mac" does not give models 32 GB. macOS, your browser, and your apps live
in the same pool. Realistic planning:

| Mac RAM | Realistic room for models | Comfortable class |
|---|---|---|
| 8 GB | ~4–5 GB | 3B–4B |
| 16 GB | ~10–11 GB | 7B–8B |
| 32 GB | ~24 GB | 14B, fast 30B-class MoE |
| 64 GB+ | ~50 GB+ | 70B class |

Close heavy apps before loading a big model, and prefer MLX-format models
([Mac guide](mac-apple-silicon.md)).

## Reading a model name

`qwen3:8b-q4_K_M` decodes as:

- `qwen3` — the family (who made it, what generation)
- `8b` — 8 billion parameters (the size class)
- `q4_K_M` — quantization level (Q4 = the standard default; see the
  [glossary](glossary.md))

If the tag has no `q…` suffix, you're usually getting Q4 anyway.

## Picking within your tier

1. **Start with the general pick for your tier** (table above, or your hardware
   guide's table — same numbers).
2. **Coding?** Use a coding model of the same size class (Qwen Coder, DeepSeek
   Coder Lite) — they're meaningfully better at code than general models.
3. **Want to see reasoning?** Try a reasoning model (Qwen3 has thinking modes;
   DeepSeek-R1 distills) — better at math/logic, slower to answer.
4. **Don't hoard.** Models are 2–20 GB each. Download one, use it for a week,
   then decide what's missing.

## Two upgrade paths worth knowing

- **MoE models** (names like `30B-A3B`): big total size but only a few billion
  parameters active per token — fast even on modest GPUs *if* you have the memory
  to hold them. The trick for RAM-rich, GPU-poor machines.
- **Offloading**: runners can split a model between GPU and CPU RAM when it
  doesn't fully fit. It works, but speed drops sharply — a smaller fully-on-GPU
  model usually feels better.

*Model recommendations here are as of mid-2026 — the What's New feed on the front
page is the living version of this advice.*

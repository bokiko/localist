# CPU-Only Path — yes, it works

No GPU? Intel Mac? Integrated graphics? You can still run real models. Set your
expectations right and this is genuinely useful — not a toy.

## What to expect

- **Small models (3–4B parameters)** run at comfortable reading speed on a modern laptop
- **7–8B models** work on 16 GB RAM machines — slower, but fine for "ask a question,
  get an answer" use
- Long documents and big context windows are where CPU hurts most — keep prompts short

| System RAM | First model to run | Feels like |
|---|---|---|
| 8 GB | `qwen3:1.7b` or `phi4-mini` | Quick answers, light chat |
| 16 GB | `qwen3:4b` | Solid daily assistant |
| 32 GB | `qwen3:8b` | Good quality, patient pace |

*(Model landscape moves fast — the What's New feed on the front page tracks new releases.)*

## Step 1: Install Ollama

- **Windows / Mac:** installer from [ollama.com/download](https://ollama.com/download)
- **Linux:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

## Step 2: Run a small model

```bash
ollama run qwen3:4b
```

First run downloads a couple of GB. Then chat directly in the terminal.

**Prefer an app?** [LM Studio](https://lmstudio.ai) does the same with a GUI and
shows you *before downloading* whether a model fits your RAM.

## Tricks that matter more on CPU

1. **Stay quantized at Q4.** The default downloads are already Q4 — good. Resist
   "higher quality" Q8 variants; on CPU the speed cost isn't worth it.
2. **Smaller + newer beats bigger + older.** A current 4B model beats a two-year-old
   13B model in most tasks — and runs much faster. Check the What's New feed.
3. **Close the RAM hogs.** Browsers eat gigabytes. Models need contiguous memory.
4. **Try MoE models.** Mixture-of-experts models (e.g. the 30B-A3B class) activate
   only a few billion parameters per token — surprisingly fast on CPU if you have
   the RAM to hold them.

## When to upgrade, honestly

CPU-only is a great way to learn the ecosystem for free. If it clicks and you want
faster/bigger: a used RTX 3060 12GB is the classic budget entry, a used RTX 3090
24 GB is the enthusiast value pick, and 24 GB Radeons are the value alternative
([AMD guide](amd-gpu.md)).

## Where to go next

- **Nicer interface:** [Open WebUI](https://github.com/open-webui/open-webui)
- **Transcription:** [whisper.cpp](https://github.com/ggml-org/whisper.cpp) is
  famously CPU-friendly — real-time transcription without any GPU
- **Stuck?** [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)

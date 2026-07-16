# Mac (Apple Silicon) Path — zero to chatting in 10 minutes

M1, M2, M3, or M4 — any of them. Apple Silicon is quietly one of the best local-AI
platforms: the **unified memory** means your Mac's RAM *is* your GPU memory, and
Apple's **MLX** framework makes models load faster and run quicker than generic backends.

## Step 0: Check your RAM

Apple menu → **About This Mac** → Memory.

| RAM | Your tier | First model to try |
|---|---|---|
| 8 GB | Tight but works | Phi-4 Mini or Qwen3 4B |
| 16 GB | Sweet spot entry | Qwen3 8B (≈11 GB is usable for models after macOS takes its share) |
| 32 GB | Genuinely powerful | Qwen3 14B, or the fast 30B-class MoE models |
| 64 GB+ | Big leagues | 70B-class models run comfortably |

*(Model landscape moves fast — the What's New feed on the front page tracks new releases.)*

## Step 1: Install LM Studio (the no-terminal route)

1. Download from [lmstudio.ai](https://lmstudio.ai) (free)
2. Open it, click the search icon, and find a model from your tier above
3. **Prefer models tagged `MLX`** — LM Studio runs these on Apple's own framework,
   which loads models faster and generates noticeably quicker than the generic
   (GGUF) version of the same model
4. Download, click chat, done

That's genuinely it. LM Studio handles memory fitting and warns you if a model
is too big for your Mac.

## Alternative: Ollama (the terminal route)

If you're comfortable in Terminal and want the tool the rest of the ecosystem
plugs into:

```bash
brew install ollama
ollama run qwen3:8b
```

Ollama gives you a local API at `localhost:11434` that other apps
(coding assistants, web UIs) can connect to.

## Things Mac people should know

- **Unified memory rule of thumb:** macOS + apps need ~4–5 GB; whatever remains is
  what models can use. A 16 GB Mac realistically fits models up to ~11 GB on disk.
- **MLX vs GGUF:** same models, two formats. MLX is Apple-optimized — prefer it when
  offered. GGUF is the universal format — works fine here too, just not as fast.
- **The Neural Engine isn't used** for LLMs — inference runs on the GPU via Metal.
  That's normal and expected.
- **Battery:** local inference is heavy. On a MacBook, plug in for long sessions.

## Where to go next

- **ChatGPT-style web interface:** [Open WebUI](https://github.com/open-webui/open-webui)
  on top of Ollama
- **Coding assistant:** [Aider](https://github.com/Aider-AI/aider) (terminal) or
  [OpenCode](https://github.com/anomalyco/opencode) pointed at LM Studio's or Ollama's local API
- **Which model size fits your Mac:** [choosing models](choosing-models.md)
- **Whisper transcription:** [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
  is excellent on Apple Silicon
- **Stuck?** [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) is the community hub

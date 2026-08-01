# NVIDIA GPU Path — zero to chatting in 15 minutes

*Unfamiliar word? The [glossary](glossary.md) explains every term here in plain English.*

You have an NVIDIA GeForce card. This is the smoothest road in local AI — everything
supports CUDA out of the box.

## Step 0: Check your VRAM

Open a terminal (PowerShell on Windows) and run:

```
nvidia-smi
```

Look at the memory column (e.g. `12288MiB` = 12 GB). Find your tier:

| VRAM | Your tier | First model to run |
|---|---|---|
| 6–8 GB | Starter | `qwen3:4b` |
| 10–12 GB | Solid | `qwen3:8b` |
| 16 GB | Strong | `qwen3:14b` |
| 24 GB (3090/4090) | Enthusiast | `qwen3:32b` or `gemma3:27b` |
| 32 GB (5090) | Top tier | `qwen3:32b` with plenty of context headroom |

*(Model landscape moves fast — the Fresh updates feed on the front page tracks new releases.)*

## Step 1: Install Ollama

**Windows:** download the installer from [ollama.com/download](https://ollama.com/download)

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

*(Prefer not to pipe scripts into your shell? Use the manual install steps on
[ollama.com/download](https://ollama.com/download) instead — same result.)*

## Step 2: Run your first model

```bash
ollama run qwen3:8b
```

(Swap in the model from your tier table above.) First run downloads the model
(a few GB — one-time). Then you're chatting, right in the terminal.

Sanity check that it's using your GPU: in another terminal, run

```bash
ollama ps
```

The **PROCESSOR** column should say `100% GPU`. If it says something like
`38%/62% CPU/GPU`, the model was too big to fit and part of it is running on
your CPU — that's why it feels slow. Drop down one model size.

(`nvidia-smi` is worth a look too, but it can't tell you this: it shows the
`ollama` process holding VRAM whether the model is fully resident or only
half of it is.)

## Step 3: Get a real interface (optional but recommended)

Terminal chat gets old. [Open WebUI](https://github.com/open-webui/open-webui) gives
you a ChatGPT-style interface on top of Ollama.

With [Docker](https://docs.docker.com/get-docker/) installed:

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Open [http://localhost:3000](http://localhost:3000), create a local account, and chat.

**Prefer no terminal at all?** [LM Studio](https://lmstudio.ai) is a desktop app that
does everything (download, manage, chat) with clicks instead of commands.

## Step 4: Understand what you just did

- Ollama downloaded a **quantized** model — compressed to fit consumer GPUs with
  minimal quality loss ([glossary](glossary.md) explains quantization)
- The model runs **entirely on your machine** — unplug the internet and it still works
- Ollama also started a **local API** at `localhost:11434` — any app that speaks the
  OpenAI API format can now use your local model

## Where to go next

- **Bigger/other models:** browse [ollama.com/library](https://ollama.com/library) —
  rule of thumb: model file size should be at most ~80% of your VRAM.
  Watch the units when you do this sum: ollama.com lists sizes in decimal GB,
  which reads about 7% larger than the GiB your card actually reports. A model
  listed as "20GB" is 18.8 GiB — comparing the two directly will make a model
  look bigger than it is
- **Coding assistant:** [Aider](https://github.com/Aider-AI/aider) (terminal) or
  [OpenCode](https://github.com/anomalyco/opencode) pointed at your Ollama instance
- **Which model size fits your card:** [choosing models](choosing-models.md)
- **Image generation:** [ComfyUI](https://github.com/Comfy-Org/ComfyUI) —
  NVIDIA cards are first-class citizens there too
- **Stuck?** [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) is the community hub

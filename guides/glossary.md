# Glossary — local AI in plain words

Every term you'll bump into, explained without jargon. Skim it once; come back
when a model name like `qwen3:8b-q4_K_M` stops making sense.

## The basics

**LLM (Large Language Model)** — the AI itself. A single file of learned numbers
("weights") that predicts text. ChatGPT runs one in the cloud; you're about to run
one on your machine.

**Weights** — the numbers inside that file. They're what the model *learned* during
training, and together they're the model: download the weights and you have it,
permanently, offline. Everything else — Ollama, LM Studio — is just a program that
loads them and does the maths. It's also why models are big: "8 billion parameters"
means 8 billion of these numbers to store.

**Model parameters (the "B" numbers)** — `qwen3:8b` means 8 **b**illion parameters.
More parameters ≈ smarter but bigger and slower. 3–4B is small, 7–14B is mid,
30B+ is large, 70B+ is huge.

**Inference** — running the model to get answers. (Training is how it was created —
you won't be doing that.)

**Token** — the chunk models read and write text in; roughly ¾ of a word.
"Hello world" ≈ 2–3 tokens.

**Tokens per second (tok/s)** — generation speed. 10 tok/s reads like a slow typist,
30+ feels instant, 100+ is faster than you can read.

## Fitting models on your machine

**VRAM** — your GPU's own memory. **The** number that decides which models you can
run. Not the same as system RAM.

**Unified memory** — Apple Silicon's trick: RAM and GPU memory are the same pool,
so a 32 GB Mac can run models a 12 GB-VRAM PC can't.

**Quantization** — compressing a model to fit smaller hardware, like a high-quality
JPEG of the original. Cuts size 4× with a small quality cost. It's why a 8B model
fits in 5 GB instead of 16 GB.

**Q4 / Q5 / Q8 (e.g. `q4_K_M`)** — quantization levels. The number ≈ bits per
parameter: Q4 = strong compression (the standard default), Q8 = nearly lossless but
twice the size. Start with Q4; only step up if you notice quality issues.

**The `_K_M` bit (as in `q4_K_M`)** — you can safely ignore it, but here's what it
says. **K** is the modern compression method (the older one had no letter). **M** is
the size within that method: **S**mall, **M**edium, **L**arge. M spends a few extra
bits on the parts of the model that matter most, so it's slightly bigger and slightly
better than S. It's the one almost everyone ships as the default — if you see a model
with no `q…` label at all, this is usually what you're getting.

**Offloading** — when a model is too big for your GPU, the runner can put *part* of it
on the GPU and leave the rest in ordinary system RAM. It works, and it's why an
oversized model still "runs" instead of refusing — but the part on the CPU is far
slower, so the whole thing crawls. This is the usual reason a model that technically
loads feels unusably slow. A smaller model that fits entirely on the GPU almost always
feels better. See [choosing models](choosing-models.md).

**GGUF** — the universal file format for quantized models. If a tool runs local
models, it almost certainly reads GGUF.

**MLX** — Apple's model format/framework. Same models, optimized for Apple Silicon:
faster loading and generation than GGUF on a Mac.

**Context window** — the model's short-term memory, measured in tokens. A 32k
context ≈ 24,000 words it can "see" at once. Bigger contexts use more memory and
slow things down.

## The tools

**Ollama** — the beginner-standard model runner. One command to install, one to run
a model. Everything else can plug into it.

**llama.cpp** — the engine underneath most local-AI tools (including Ollama).
You'll use it directly only when you want maximum control.

**LM Studio** — desktop app that wraps everything in a GUI: browse models, download,
chat. No terminal.

**Open WebUI** — a ChatGPT-lookalike web interface that sits on top of Ollama.

**API** — a way for one program to talk to another without a human in the middle.
Not something you use directly; it's what lets a *different* app (a notes app, a
code editor) send questions to your model and get answers back.

**Local API / OpenAI-compatible API** — most runners quietly offer one of these at an
address like `localhost:11434`. `localhost` means "this computer, not the internet" —
the address only works on your own machine, and nothing is being published. It's
called *OpenAI-compatible* because it speaks the same format ChatGPT's service does,
which is the useful part: apps built to talk to ChatGPT can be pointed at your local
model instead, usually by pasting that address into a settings box.

**RAG (Retrieval-Augmented Generation)** — "chat with your documents." The app
finds the relevant passages from files you give it and hands them to the model
along with your question, so answers can draw on your own notes, PDFs, or code —
not just what the model memorized in training. AnythingLLM and Open WebUI's
Knowledge feature do this for you.

## Model-picking vocabulary

**Instruct / chat model** — tuned to follow instructions and converse. This is what
you want. (A "base" model just continues text — not useful for chat.)

**Reasoning model** — "thinks" step-by-step before answering (you often see the
thinking). Better at math/logic, slower to respond.

**MoE (Mixture of Experts)** — a model built from many small specialists where only
a few activate per token. Big total size, but fast — great when you have RAM but a
weak GPU. Names like `30B-A3B` mean "30B total, 3B active."

**Distilled / mini / tiny models** — small models taught by bigger ones. The reason
today's 4B models beat yesterday's 13B ones.

**Benchmarks (MMLU, HumanEval, …)** — standardized test scores you'll see in model
announcements. Useful for rough comparison, gameable, never the whole story. Trust
your own use more than a leaderboard.

**Uncensored / abliterated** — community-modified models with refusals removed.
They exist; quality varies wildly.

## Hardware vocabulary

**CUDA** — NVIDIA's GPU-compute layer. The reason NVIDIA "just works" everywhere.

**ROCm** — AMD's answer to CUDA. Recent versions are supported by the major
local-AI tools; exact compatibility depends on your GPU model and OS.

**Vulkan** — a graphics API that doubles as an easy GPU path for AMD/Intel cards —
slightly slower than ROCm/CUDA, dramatically less setup.

**Metal** — Apple's GPU layer. What actually runs models on a Mac (not the
Neural Engine, despite the marketing).

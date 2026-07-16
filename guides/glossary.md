# Glossary — local AI in plain words

Every term you'll bump into, explained without jargon. Skim it once; come back
when a model name like `qwen3:8b-q4_K_M` stops making sense.

## The basics

**LLM (Large Language Model)** — the AI itself. A single file of learned numbers
("weights") that predicts text. ChatGPT runs one in the cloud; you're about to run
one on your machine.

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

**Local API / OpenAI-compatible API** — most runners expose an interface at an
address like `localhost:11434` that mimics OpenAI's. Any app built for ChatGPT's
API can be pointed at your local model instead.

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

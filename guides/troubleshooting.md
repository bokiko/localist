# Troubleshooting — when it doesn't just work

Find what you're seeing on screen. Each fix is the shortest thing that works.

Nothing here can break your computer. The worst case is deleting a model file and
downloading it again.

**Jump to:** [Where do I type this?](#the-guide-gave-me-a-command-and-i-dont-know-where-to-type-it) ·
[How do I stop?](#how-do-i-stop-the-chat) ·
[How do I get back tomorrow?](#how-do-i-get-back-tomorrow) ·
[Installing](#the-install-didnt-take) · [Downloading](#the-download-is-stuck) ·
[Speed and memory](#its-running-but-something-is-wrong) ·
[Still stuck](#still-stuck)

---

## The guide gave me a command and I don't know where to type it

You're looking at a grey box like this, and there's nowhere on the page to put it:

```bash
ollama run qwen3:4b
```

That goes in a **terminal** — a plain window where you type commands instead of
clicking. Every computer already has one; you just haven't needed it before.

**Open it:**
- **Windows:** press `Start`, type `powershell`, press Enter
- **Mac:** press `Cmd` + `Space`, type `terminal`, press Enter
- **Linux:** `Ctrl` + `Alt` + `T` on most desktops

A window opens with a blinking cursor. **Type the command there and press Enter.**
You can copy and paste it — right-click pastes in PowerShell,
`Cmd` + `V` on Mac, `Ctrl` + `Shift` + `V` in most Linux terminals.

Nothing you type in a terminal is dangerous by itself, and nothing here will change
your system beyond installing the program you asked for.

**Would rather not use a terminal at all?** [LM Studio](https://lmstudio.ai) does all
of this — download a model, chat with it — with buttons instead of commands. It's a
normal desktop app. Both the Mac and AMD guides start there.

---

## How do I stop the chat?

You're at a prompt that looks like this and nothing you type ends it:

```
>>> Send a message (/? for help)
```

**Type `/bye` and press Enter.** That's it — you're back at your normal terminal.

`Ctrl` + `D` does the same thing. So does `/exit`. If you press `Ctrl` + `C`,
Ollama will remind you: *"Use Ctrl + d or /bye to exit."*

Closing the terminal window also works and breaks nothing.

**Stopping the chat does not delete the model.** It stays on your disk, ready to go.
You only download it once.

## How do I get back tomorrow?

The model is still there. You need two things: a terminal, and one command.

**Open a terminal**
- **Windows:** press `Start`, type `powershell`, press Enter
- **Mac:** press `Cmd` + `Space`, type `terminal`, press Enter
- **Linux:** `Ctrl` + `Alt` + `T` on most desktops

**Then run the same command you ran the first time:**

```bash
ollama run qwen3:4b
```

Use whichever model name your hardware guide gave you. It starts in seconds this
time — no download, because you already have it.

**Forgotten which models you have?** This lists them:

```bash
ollama list
```

**Using LM Studio instead?** Just open the app. Your model and your chats are
still in it — there's nothing to re-run.

---

## The install didn't take

### `'ollama' is not recognized` / `command not found: ollama`

You'll see one of these:

```
ollama : The term 'ollama' is not recognized as the name of a cmdlet...   (Windows)
zsh: command not found: ollama                                            (Mac/Linux)
```

Your terminal doesn't know where Ollama is. Almost always one of two things:

1. **You opened the terminal before installing.** Close it, open a new one, try
   again. A terminal only learns about new programs when it starts.
2. **The installer didn't finish.** Re-run it from
   [ollama.com/download](https://ollama.com/download) and watch for an error at the end.

### `could not connect to ollama server`

```
could not connect to ollama server, run 'ollama serve' to start it
```

Ollama is installed, but the background part isn't running.

- **Easiest fix:** run `ollama serve` in a *second* terminal window, leave it open,
  and go back to your first window.
- **Mac, if you installed with Homebrew:** Homebrew doesn't start it for you. Run
  `brew services start ollama` once and it will start on its own from now on.
- **Windows/Mac, if you used the installer:** look for the Ollama icon in your
  system tray or menu bar. If it isn't there, launch Ollama from your applications.

### Windows blocked the installer

A blue box saying *"Windows protected your PC"*, or the download vanishing.

This is SmartScreen or your antivirus reacting to a newly-downloaded installer,
not evidence of a problem. Click **More info → Run anyway** — but only if you
downloaded it from [ollama.com](https://ollama.com/download) or
[lmstudio.ai](https://lmstudio.ai) yourself. If you're not certain where the file
came from, delete it and download it again from the official site.

---

## The download is stuck

### It sits on the same percentage for a long time

Model files are gigabytes. On a normal home connection the first download takes
**5 to 30 minutes**. A progress bar that moves slowly is working.

If it's genuinely frozen — no change for several minutes — press `Ctrl` + `C`,
then run the same command again. **It resumes where it left off**; you don't
start over.

### It failed partway with a network error

Same fix: run the command again. Downloads resume.

If it keeps failing at the same point, you're likely out of disk space — see below.

### "No space left" / the download dies near the end

Check you have room. Models are 1–20 GB each, and you need the space *free*, not
just "nearly free".

To see what you've downloaded and reclaim space:

```bash
ollama list           # what you have
ollama rm qwen3:8b    # delete one you don't want
```

---

## It's running, but something is wrong

### Answers come out one word every few seconds

This is the normal speed range on a CPU-only machine, and it's why the CPU guide
suggests small models. If it's slower than you can stand:

1. **Use a smaller model.** Dropping from 8B to 4B roughly doubles the speed.
2. **Close your browser.** Browsers hold gigabytes. Models need free memory.
3. **Keep prompts short.** Pasting a long document is the slowest thing you can do.

### The computer freezes, fans roar, or the model quits on its own

The model is too big for your memory. Nothing is damaged — your machine ran out of
room and gave up.

Use the next size down. If you were on `qwen3:8b`, try `qwen3:4b`; from `4b`, try
`qwen3:1.7b`. Your hardware guide's table lists the right size for your memory, and
[choosing models](choosing-models.md) explains why.

### It answers, but the answers are strange, repetitive, or cut off

- **Repetitive or looping:** normal for very small models on hard questions. Ask
  something simpler to confirm it's working, then use a bigger model if you have
  the memory for it.
- **Cut off mid-sentence:** you've filled the context window — the model's
  short-term memory. Start a fresh chat; long conversations fill it up.
- **Confidently wrong:** expected, and not a bug you can fix. Local models are
  smaller than cloud ones. See
  [what to expect](start-here.md#what-this-will-and-wont-do-well).

### LM Studio won't let me load a model

LM Studio checks whether a model fits your machine before it loads it, and greys
out or warns on ones that don't. That warning is doing you a favour — pick a
smaller model from the same family.

---

## Still stuck

- Re-read your hardware guide's step 1 from the top. Most failures are a skipped step.
- Restart the computer. It genuinely fixes the "installed but not found" cases.
- Ask at [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) — say what you typed, what
  you saw, and what machine you're on. **Remove anything private first:** file paths
  with your name in them, keys, or screenshots of other windows.
- Think a page here is wrong or out of date?
  [Tell us](https://github.com/bokiko/localist/issues/new?template=report-stale.yml) —
  please don't paste anything private into a public issue.

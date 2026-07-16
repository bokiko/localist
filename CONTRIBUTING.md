# Contributing to Localist

Thanks for helping keep this useful. Localist is deliberately **small and opinionated** —
the bar for adding things is high, and removing dead things is as valued as adding new ones.

## Suggest a tool

Open a [suggest-tool issue](../../issues/new?template=suggest-tool.yml). For a tool
to be listed it should be:

1. **Runnable locally** — no cloud dependency for its core function
2. **Alive** — commits or releases within the last 3 months
3. **Beginner-relevant** — either directly usable by a newcomer, or the clear next
   step after the basics
4. **Better or different** — not a near-duplicate of an existing entry

"It's on GitHub and has stars" is not enough. Tell us *who* it's for and *why*
it beats (or complements) the current pick in its category.

## Report a stale entry

Tool abandoned? Instructions broken? Model recommendation outdated? Open a
[report-stale issue](../../issues/new?template=report-stale.yml). This is the most
valuable contribution of all — most lists rot because nobody does this.

## Fix or improve a guide

PRs to `guides/` are welcome: clearer wording, corrected commands, updated model
recommendations (cite a source for volatile claims like benchmarks or version
numbers).

## What NOT to submit

- **Self-promotion without disclosure** — say so if it's your project (that's fine!)
- **Exhaustive lists** — we link the best, not everything; other lists do that well
- **Edits to the What's New block or `news/`** — those are pipeline-generated;
  edit `scripts/` or `data/watchlist.yml` instead
- **Manual edits to `data/seen.json`** — pipeline state

## How curation works

All curated entries live in [`data/curated.yml`](data/curated.yml) — one entry per
tool with a category, tags, and a one-line *why*. Each category has exactly one
`pick: true`. The README Essentials table reflects those picks. To propose changing
a pick, open an issue and make the case.

## Licensing of contributions

- Code contributions (`scripts/`, `tests/`, `.github/`) are accepted under [MIT](LICENSE)
- Content contributions (`guides/`, README prose, entry descriptions) under
  [CC-BY-4.0](LICENSE-CONTENT)

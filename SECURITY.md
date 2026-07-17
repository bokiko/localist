# Security Policy

Localist is a content + tooling repository: beginner guides plus a small Python
pipeline that updates the README and news archive via GitHub Actions.

## Reporting a vulnerability

If you find a security issue — for example in the update pipeline, the GitHub
Actions workflows, or a guide that recommends something unsafe — please report
it privately rather than opening a public issue:

- Use GitHub's **private vulnerability reporting** on this repository
  (Security tab → "Report a vulnerability"), or
- Contact the maintainer directly via the profile at
  [github.com/bokiko](https://github.com/bokiko).

You can expect an acknowledgment within a few days. Please give us a
reasonable window to fix the issue before disclosing it publicly.

## Scope notes

- The pipeline runs with the repository's default `GITHUB_TOKEN` only; it
  holds no other secrets.
- Guides may link to third-party tools and install scripts. We vet what we
  recommend, but those projects have their own security policies — issues in
  them should be reported upstream. If a *recommendation itself* is unsafe,
  that's in scope here.

"""PR-1.5 repo security baseline: enforce local-only protection in every clone.

These are the tracked-file / history / ignore-rule gates from the security
addendum, encoded as CI-enforced tests. The principle: catch sensitive material
at commit/push time, because git history is forever. If any of these fail, do
NOT push — stop and remediate.
"""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Paths that must never be tracked. CLAUDE.md holds machine/infra context and is
# not committed until sanitized + explicitly approved.
SENSITIVE_TRACKED = ["thoughts/", ".env", ".env.*", "CLAUDE.md"]

# Patterns the COMMITTED .gitignore must contain so protection travels to every
# clone (a .git/info/exclude entry is local-only and does not count).
REQUIRED_IGNORE_PATTERNS = [
    "thoughts/",
    ".env",
    ".env.*",
    "CLAUDE.md",
    "site/node_modules/",
    "site/dist/",
    "site/.astro/",
    "site/src/content/generated/",
]


def _git(*args):
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()


def test_no_sensitive_files_are_tracked():
    tracked = _git("ls-files", *SENSITIVE_TRACKED)
    assert tracked == "", (
        f"local-only files are TRACKED (must be untracked): {tracked!r}"
    )


def test_local_only_files_never_in_history():
    hist = _git("log", "--all", "--oneline", "--", "thoughts/", ".env", "CLAUDE.md")
    assert hist == "", (
        f"thoughts/, .env, or CLAUDE.md appear in git history — remediation required: {hist!r}"
    )


def test_committed_gitignore_covers_local_only_and_build_outputs():
    gitignore = (REPO / ".gitignore").read_text().splitlines()
    entries = {line.strip() for line in gitignore if line.strip() and not line.startswith("#")}
    missing = [p for p in REQUIRED_IGNORE_PATTERNS if p not in entries]
    assert not missing, (
        f".gitignore is missing required patterns (protection would not travel to a "
        f"fresh clone): {missing}"
    )


def test_sensitive_paths_are_actually_ignored():
    # git check-ignore exits 0 when the path IS ignored
    for path in ["thoughts/", ".env", "CLAUDE.md"]:
        r = subprocess.run(
            ["git", "check-ignore", "-q", path], cwd=REPO
        )
        assert r.returncode == 0, f"{path} is NOT ignored by any rule"

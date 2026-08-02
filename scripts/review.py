"""
Automated VN guide review loop.
Runs after guide_gen.py. For each game that has guides but unreviewed routes:
  Round loop (max MAX_REVIEW_ROUNDS):
    1. Run guide-reviewer agent in a fresh claude session (no --resume)
    2. Check for open route-accuracy GitHub issues for this slug
    3. If issues open: run guide-author agent in a fresh claude session (no --resume)
    4. Deploy after each author round so fixes are immediately visible
    5. Repeat until no open issues or max rounds reached
  On a clean reviewer pass: mark all routes reviewed=true in guide.json

Author and reviewer are always separate claude invocations with no shared session
and no shared context. This is the adversarial property that makes the review useful.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_PATH = Path(os.environ.get("REPO_PATH", "/app/repo"))
SCRIPTS_PATH = Path(__file__).parent
GAMES_JSON = REPO_PATH / "games.json"

MODEL = os.environ.get("GUIDE_REVIEW_MODEL", "claude-sonnet-5")
MAX_TURNS = int(os.environ.get("GUIDE_REVIEW_MAX_TURNS", "60"))
MAX_REVIEW_ROUNDS = int(os.environ.get("GUIDE_REVIEW_MAX_ROUNDS", "5"))
TIMEOUT_REVIEW = int(os.environ.get("GUIDE_REVIEW_TIMEOUT", str(3600)))


def log(msg: str) -> None:
    print(f"[review] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[review] {msg}", file=sys.stderr, flush=True)


def run_deploy() -> None:
    result = subprocess.run(
        ["python3", str(SCRIPTS_PATH / "deploy.py")],
        cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err("Deploy failed — changes saved locally, will push on next cycle")


def run_claude_fresh(prompt: str, timeout: int = TIMEOUT_REVIEW) -> bool:
    """Invoke claude CLI in a completely fresh session (no --resume).

    Each call starts with no context from any prior call — author and reviewer
    never share a session, so neither can be biased by the other's framing.
    """
    cmd = [
        "claude",
        "-p", prompt,
        "--dangerously-skip-permissions",
        "--model", MODEL,
        "--max-turns", str(MAX_TURNS),
    ]
    try:
        result = subprocess.run(cmd, cwd=str(REPO_PATH), timeout=timeout)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        err(f"Claude timed out after {timeout}s")
        return False
    except FileNotFoundError:
        err("claude CLI not found — is @anthropic-ai/claude-code installed?")
        return False


def has_open_issues(slug: str) -> bool:
    """Return True if any route-accuracy GitHub issues are open for this slug."""
    result = subprocess.run(
        ["gh", "issue", "list",
         "--label", "route-accuracy",
         "--label", slug,
         "--state", "open",
         "--json", "number"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err(f"gh issue list failed: {result.stderr.strip()}")
        return False
    try:
        return len(json.loads(result.stdout or "[]")) > 0
    except json.JSONDecodeError:
        return False


def mark_all_reviewed(guide_file: Path) -> None:
    """Set reviewed=true on every route in guide.json."""
    guide = json.loads(guide_file.read_text())
    for route in guide.get("routes", []):
        route["reviewed"] = True
    guide_file.write_text(json.dumps(guide, ensure_ascii=False, indent=2))
    log(f"All routes marked reviewed: {guide_file.relative_to(REPO_PATH)}")


def review_game(slug: str) -> None:
    guide_file = REPO_PATH / slug / "guide.json"

    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(f"Review round {round_num}/{MAX_REVIEW_ROUNDS} for {slug}")

        # Reviewer runs in a fresh session — no context from author or prior rounds
        reviewer_prompt = (
            f"Read .claude/agents/guide-reviewer.md and follow those instructions exactly. "
            f"You are reviewing the guide for '{slug}'. "
            f"Check all routes in {slug}/guide.json and their route_*.json files. "
            f"Fetch both primary Japanese sources listed in {slug}/research.json. "
            f"Create a GitHub issue for every problem you find. "
            f"If no problems are found, confirm with: "
            f"gh issue list --label route-accuracy --label {slug} --state open"
        )
        ok = run_claude_fresh(reviewer_prompt)
        if not ok:
            err(f"Reviewer failed for {slug} round {round_num} — will retry next cycle")
            return

        if not has_open_issues(slug):
            log(f"No open issues for {slug} — marking all routes as reviewed")
            mark_all_reviewed(guide_file)
            run_deploy()
            return

        if round_num == MAX_REVIEW_ROUNDS:
            log(f"Reached max rounds ({MAX_REVIEW_ROUNDS}) for {slug} — manual review needed")
            return

        log(f"Open issues found for {slug} — running author to fix (round {round_num})")

        # Author runs in a fresh session — no context from reviewer
        author_prompt = (
            f"Read .claude/agents/guide-author.md and follow those instructions exactly. "
            f"Fix all open GitHub issues labeled 'route-accuracy' and '{slug}'. "
            f"List them first: gh issue list --label route-accuracy --label {slug} --state open "
            f"Then read each issue with: gh issue view <number> "
            f"Apply each fix to the guide file, then close the issue with: "
            f"gh issue close <number> --comment \"Fixed: <description>\""
        )
        ok = run_claude_fresh(author_prompt)
        if not ok:
            err(f"Author failed for {slug} round {round_num} — will retry next cycle")
            return

        run_deploy()


def run() -> None:
    if not GAMES_JSON.exists():
        log("games.json not found, skipping")
        return

    if subprocess.run(["gh", "--version"], capture_output=True).returncode != 0:
        err("gh CLI not found — skipping review pass (install GitHub CLI to enable automated review)")
        return

    games = json.loads(GAMES_JSON.read_text())
    reviewed_any = False

    for vid, entry in games.items():
        if not entry.get("has_guide"):
            continue
        slug = entry["slug"]
        guide_file = REPO_PATH / slug / "guide.json"
        if not guide_file.exists():
            continue

        try:
            guide = json.loads(guide_file.read_text())
        except json.JSONDecodeError:
            continue

        unreviewed = [r for r in guide.get("routes", []) if r.get("reviewed") is not True]
        if not unreviewed:
            log(f"{slug}: all routes reviewed")
            continue

        log(f"{slug}: {len(unreviewed)} unreviewed route(s) — starting review loop")
        review_game(slug)
        reviewed_any = True

    if not reviewed_any:
        log("Nothing to review")


if __name__ == "__main__":
    run()

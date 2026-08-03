"""
Automated VN guide review loop.
Runs after guide_gen.py. For each game that has guides but unreviewed routes:
  For each unreviewed route:
    Round loop (max MAX_REVIEW_ROUNDS):
      1. Check for a pre-existing open issue for this route
      2. If none: run reviewer for this route; if still no issue → mark reviewed
      3. If issue open: run author to fix it, deploy, then re-review
      4. Repeat until issue closes or max rounds reached
  Each route is reviewed in its own fresh claude session — never batched.

GUIDE_PRIORITY_VID: only process this game (same env var as guide_gen.py).
GUIDE_REVIEW_ROUTE: only process this route id within the priority game (for testing).

Author and reviewer are always separate claude invocations with no shared session.
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


def get_open_issue_for_route(slug: str, route_id: str, route_title: str = "") -> int | None:
    """Return issue number if an open route-accuracy issue exists for this route.

    Matches on route_id OR route_title because the reviewer uses the display title
    (e.g. '沖田総司ルート') in the issue title, not the internal id ('okita').
    """
    result = subprocess.run(
        ["gh", "issue", "list",
         "--label", "route-accuracy",
         "--label", slug,
         "--state", "open",
         "--json", "number,title"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err(f"gh issue list failed: {result.stderr.strip()}")
        return None
    try:
        issues = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return None
    for issue in issues:
        title = issue.get("title", "").lower()
        if route_id in title or (route_title and route_title.lower() in title):
            return issue["number"]
    return None


def mark_route_reviewed(guide_file: Path, route_id: str) -> None:
    guide = json.loads(guide_file.read_text())
    for route in guide.get("routes", []):
        if route["id"] == route_id:
            route["reviewed"] = True
    guide_file.write_text(json.dumps(guide, ensure_ascii=False, indent=2))
    log(f"Route {route_id} marked reviewed in {guide_file.relative_to(REPO_PATH)}")


def review_route(slug: str, route_id: str, route_title: str) -> bool:
    """Run the review loop for a single route. Returns True if route passes."""
    guide_file = REPO_PATH / slug / "guide.json"

    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(f"Route {route_id}: round {round_num}/{MAX_REVIEW_ROUNDS}")

        existing_issue = get_open_issue_for_route(slug, route_id, route_title)

        if existing_issue is None:
            # No open issue — run fresh reviewer for this route
            log(f"Route {route_id}: no open issue — running reviewer")
            reviewer_prompt = (
                f"Read .claude/agents/guide-reviewer.md and follow those instructions exactly. "
                f"Review the '{route_title}' route for the game '{slug}'. "
                f"The route file is {slug}/route_{route_id}.json. "
                f"Fetch both primary Japanese sources listed in {slug}/research.json. "
                f"If you find accuracy issues, create exactly ONE GitHub issue with: "
                f"  title: '[{slug}] {route_title}: accuracy review' "
                f"  labels: route-accuracy and {slug} "
                f"  body: all findings for this route "
                f"If no issues are found, do not create a GitHub issue."
            )
            ok = run_claude_fresh(reviewer_prompt)
            if not ok:
                err(f"Reviewer failed for {slug}/{route_id} round {round_num} — will retry next cycle")
                return False

            existing_issue = get_open_issue_for_route(slug, route_id, route_title)
            if existing_issue is None:
                log(f"Route {route_id}: reviewer found no issues — passed")
                return True

        if round_num == MAX_REVIEW_ROUNDS:
            log(f"Route {route_id}: reached max rounds ({MAX_REVIEW_ROUNDS}) — manual review needed")
            return False

        # Open issue exists — run author to fix it
        log(f"Route {route_id}: issue #{existing_issue} open — running author (round {round_num})")
        author_prompt = (
            f"Read .claude/agents/guide-author.md and follow those instructions exactly. "
            f"Fix GitHub issue #{existing_issue} for the '{route_title}' route in '{slug}'. "
            f"First read the issue: gh issue view {existing_issue} "
            f"Apply all required fixes to {slug}/route_{route_id}.json. "
            f"When done, close the issue: "
            f"gh issue close {existing_issue} --comment \"Fixed: <one-line description of what changed>\""
        )
        ok = run_claude_fresh(author_prompt)
        if not ok:
            err(f"Author failed for {slug}/{route_id} round {round_num} — will retry next cycle")
            return False

        run_deploy()

        # Re-review: verify the fix, comment or close the existing issue
        log(f"Route {route_id}: re-reviewing after author corrections (round {round_num})")
        re_reviewer_prompt = (
            f"Read .claude/agents/guide-reviewer.md and follow those instructions exactly. "
            f"Re-review the '{route_title}' route for '{slug}' after author corrections. "
            f"First read the existing issue: gh issue view {existing_issue} "
            f"Re-fetch the relevant sections of both Japanese sources listed in {slug}/research.json. "
            f"Verify each finding in the issue was correctly fixed in {slug}/route_{route_id}.json. "
            f"If all findings are resolved: close the issue with a confirming comment. "
            f"If any finding is still wrong: add a comment to issue #{existing_issue} describing what remains, do not close it."
        )
        ok = run_claude_fresh(re_reviewer_prompt)
        if not ok:
            err(f"Re-reviewer failed for {slug}/{route_id} round {round_num} — will retry next cycle")
            return False

        # Check if the issue was closed by the re-reviewer
        still_open = get_open_issue_for_route(slug, route_id, route_title)
        if still_open is None:
            log(f"Route {route_id}: issue closed by reviewer — passed")
            return True

        log(f"Route {route_id}: issue #{still_open} still open after round {round_num}")

    return False


def review_game(slug: str, priority_route: str | None = None) -> None:
    guide_file = REPO_PATH / slug / "guide.json"

    try:
        guide = json.loads(guide_file.read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        err(f"Could not read guide.json for {slug}: {e}")
        return

    for route in guide.get("routes", []):
        if route.get("reviewed"):
            continue
        route_id = route["id"]
        if priority_route and route_id != priority_route:
            continue

        route_title = route.get("title", route_id)
        log(f"{slug}: reviewing route {route_id} ({route_title})")

        passed = review_route(slug, route_id, route_title)
        if passed:
            mark_route_reviewed(guide_file, route_id)
            run_deploy()
        else:
            log(f"{slug}/{route_id}: did not pass — will retry next cycle")


def run() -> None:
    if not GAMES_JSON.exists():
        log("games.json not found, skipping")
        return

    if subprocess.run(["gh", "--version"], capture_output=True).returncode != 0:
        err("gh CLI not found — skipping review pass (install GitHub CLI to enable automated review)")
        return

    games = json.loads(GAMES_JSON.read_text())

    # GUIDE_REVIEW_VID scopes the review loop to one game (separate from GUIDE_PRIORITY_VID
    # which controls the guide-gen exit gate in entrypoint.sh).
    priority_vid = os.environ.get("GUIDE_REVIEW_VID")
    priority_route = os.environ.get("GUIDE_REVIEW_ROUTE")

    if priority_vid:
        log(f"GUIDE_REVIEW_VID={priority_vid}: scoping review to this game only")
    if priority_route:
        log(f"GUIDE_REVIEW_ROUTE={priority_route}: scoping review to this route only")

    reviewed_any = False

    for vid, entry in games.items():
        if not entry.get("has_guide"):
            continue
        if priority_vid and vid != priority_vid:
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
        if priority_route:
            unreviewed = [r for r in unreviewed if r["id"] == priority_route]

        if not unreviewed:
            log(f"{slug}: all routes reviewed")
            continue

        log(f"{slug}: {len(unreviewed)} unreviewed route(s) — starting review loop")
        review_game(slug, priority_route=priority_route)
        reviewed_any = True

    if not reviewed_any:
        log("Nothing to review")


if __name__ == "__main__":
    run()

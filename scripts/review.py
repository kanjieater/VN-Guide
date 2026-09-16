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
import agent_runner

REPO_PATH = Path(os.environ.get("REPO_PATH", "/app/repo"))
SCRIPTS_PATH = Path(__file__).parent
GAMES_JSON = REPO_PATH / "games.json"

REVIEWER_MODEL = agent_runner.model_for("REVIEWER")
REVIEWER_EFFORT = os.environ.get("GUIDE_REVIEWER_EFFORT", "max")
STRUCTURAL_REVIEWER_MODEL = agent_runner.model_for("STRUCTURAL_REVIEWER")
STRUCTURAL_REVIEWER_EFFORT = os.environ.get("GUIDE_STRUCTURAL_REVIEWER_EFFORT", "high")
AUTHOR_MODEL = agent_runner.model_for("AUTHOR")
AUTHOR_EFFORT = os.environ.get("GUIDE_AUTHOR_EFFORT", "high")
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


def run_claude_fresh(prompt: str, model: str = REVIEWER_MODEL,
                     effort: str = REVIEWER_EFFORT,
                     timeout: int = TIMEOUT_REVIEW) -> bool:
    """Invoke claude CLI in a completely fresh session (no --resume).

    Each call starts with no context from any prior call — author and reviewer
    never share a session, so neither can be biased by the other's framing.
    """
    if agent_runner.provider() == "openrouter":
        return agent_runner.run_openrouter(prompt, model, MAX_TURNS, REPO_PATH, timeout)

    cmd = [
        "claude",
        "-p", prompt,
        "--dangerously-skip-permissions",
        "--model", model,
        "--effort", effort,
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
        raise RuntimeError(f"gh issue list failed: {result.stderr.strip()}")
    issues = parse_issues(result.stdout)
    for issue in issues:
        title = issue.get("title", "").lower()
        if route_id in title or (route_title and route_title.lower() in title):
            return issue["number"]
    return None


def parse_issues(output: str) -> list[dict]:
    issues = json.loads(output)
    if not isinstance(issues, list) or any(
        not isinstance(i, dict) or not isinstance(i.get("number"), int)
        or not isinstance(i.get("title"), str) for i in issues
    ):
        raise ValueError("Expected issue list with number and title")
    return issues


def get_open_structural_issue_for_route(slug: str, route_id: str, route_title: str = "") -> int | None:
    """Return issue number if an open route-structure issue exists for this route."""
    result = subprocess.run(
        ["gh", "issue", "list",
         "--label", "route-structure",
         "--label", slug,
         "--state", "open",
         "--json", "number,title"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh issue list (structural) failed: {result.stderr.strip()}")
    issues = parse_issues(result.stdout)
    for issue in issues:
        title = issue.get("title", "").lower()
        if route_id in title or (route_title and route_title.lower() in title):
            return issue["number"]
    return None


def structural_review_route(slug: str, route_id: str, route_title: str) -> bool:
    """Run the structural review loop for a single route. Returns True when structure passes."""
    guide_file = REPO_PATH / slug / "guide.json"

    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(f"Route {route_id}: structural round {round_num}/{MAX_REVIEW_ROUNDS}")

        existing_issue = get_open_structural_issue_for_route(slug, route_id, route_title)

        if existing_issue is None:
            log(f"Route {route_id}: no open structural issue — running structural reviewer")
            reviewer_prompt = (
                f"Read .claude/agents/guide-reviewer-structural.md and follow those instructions exactly. "
                f"Review the structure of the '{route_title}' route for the game '{slug}'. "
                f"The route file is {slug}/route_{route_id}.json. "
                f"Do NOT fetch any Japanese walkthroughs — this is a structural review only. "
                f"Trace the main route and every bad end chain. "
                f"If you find structural issues, create exactly ONE GitHub issue with: "
                f"  title: '[{slug}] {route_title}: structural review' "
                f"  labels: route-structure and {slug} "
                f"  body: all structural findings for this route. "
                f"If no structural issues are found, do not create a GitHub issue."
            )
            ok = run_claude_fresh(
                reviewer_prompt,
                model=STRUCTURAL_REVIEWER_MODEL,
                effort=STRUCTURAL_REVIEWER_EFFORT,
            )
            if not ok:
                err(f"Structural reviewer failed for {slug}/{route_id} round {round_num}")
                return False

            existing_issue = get_open_structural_issue_for_route(slug, route_id, route_title)
            if existing_issue is None:
                log(f"Route {route_id}: structural reviewer found no issues — passed")
                return True

        if round_num == MAX_REVIEW_ROUNDS:
            log(f"Route {route_id}: structural review reached max rounds — manual review needed")
            return False

        log(f"Route {route_id}: structural issue #{existing_issue} open — running author (round {round_num})")
        author_prompt = (
            f"Read .claude/agents/guide-author.md and follow those instructions exactly. "
            f"Fix GitHub issue #{existing_issue} for the '{route_title}' route in '{slug}'. "
            f"First read the issue: gh issue view {existing_issue} "
            f"Apply all required structural fixes to {slug}/route_{route_id}.json. "
            f"When done, report what you changed: "
            f"gh issue comment {existing_issue} --body \"Fixed: <one-line description of what changed>\" "
            f"Do NOT close the issue. Only the reviewer may close it, after independently "
            f"verifying your fix against the sources."
        )
        ok = run_claude_fresh(author_prompt, model=AUTHOR_MODEL, effort=AUTHOR_EFFORT)
        if not ok:
            err(f"Author failed for structural fix {slug}/{route_id} round {round_num}")
            return False

        run_deploy()

        log(f"Route {route_id}: re-reviewing structure after author corrections (round {round_num})")
        re_reviewer_prompt = (
            f"Read .claude/agents/guide-reviewer-structural.md and follow those instructions exactly. "
            f"Re-review the structure of the '{route_title}' route for '{slug}' after author corrections. "
            f"First read the existing issue: gh issue view {existing_issue} "
            f"Re-read {slug}/route_{route_id}.json and re-trace all bad end chains. "
            f"Verify each structural finding in the issue was correctly fixed. "
            f"If all findings are resolved: close the issue with a confirming comment. "
            f"If any finding is still wrong: add a comment to issue #{existing_issue} describing what remains. Do not close it."
        )
        ok = run_claude_fresh(
            re_reviewer_prompt,
            model=STRUCTURAL_REVIEWER_MODEL,
            effort=STRUCTURAL_REVIEWER_EFFORT,
        )
        if not ok:
            err(f"Structural re-reviewer failed for {slug}/{route_id} round {round_num}")
            return False

        still_open = get_open_structural_issue_for_route(slug, route_id, route_title)
        if still_open is None:
            log(f"Route {route_id}: structural issue closed — passed")
            return True

        log(f"Route {route_id}: structural issue #{still_open} still open after round {round_num}")

    return False


def mark_route_reviewed(guide_file: Path, slug: str, route_id: str, route_title: str) -> bool:
    """Set reviewed: true, but only if no open issue contradicts it.

    Re-checked here rather than trusted from the caller: a reviewer can file a
    fresh issue during the same round that decided the route passed.
    """
    blocking = (get_open_issue_for_route(slug, route_id, route_title)
                or get_open_structural_issue_for_route(slug, route_id, route_title))
    if blocking is not None:
        err(f"Refusing to mark {slug}/{route_id} reviewed — issue #{blocking} is still open")
        return False

    # Approval belongs to an independent accuracy reviewer, not the pipeline or author.
    ok = run_claude_fresh(
        f"Read prompt.md, CLAUDE.md and .claude/agents/guide-reviewer.md. "
        f"You are the independent accuracy reviewer for {slug}/{route_id} ({route_title}). "
        f"Structural and accuracy passes have completed. Independently re-fetch both Japanese "
        f"sources in {slug}/research.json and verify this route. Check GitHub for open "
        f"route-structure AND route-accuracy issues labeled {slug} for this route. "
        f"Only if both reviews pass and neither issue type is open, set reviewed: true for "
        f"{route_id} in {slug}/guide.json. This metadata approval is your only permitted "
        f"guide edit. Otherwise leave reviewed false and report findings in the existing "
        f"issue or create one if none exists. Never self-correct route content.",
        model=REVIEWER_MODEL, effort=REVIEWER_EFFORT,
    )
    blocking = (get_open_issue_for_route(slug, route_id, route_title)
                or get_open_structural_issue_for_route(slug, route_id, route_title))
    guide = json.loads(guide_file.read_text())
    if not ok or blocking is not None:
        for route in guide.get("routes", []):
            if route["id"] == route_id:
                route["reviewed"] = False
        guide_file.write_text(json.dumps(guide, ensure_ascii=False, indent=2))
        return False
    return any(r["id"] == route_id and r.get("reviewed") is True
               for r in guide.get("routes", []))


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
            ok = run_claude_fresh(reviewer_prompt, model=REVIEWER_MODEL, effort=REVIEWER_EFFORT)
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
            f"When done, report what you changed: "
            f"gh issue comment {existing_issue} --body \"Fixed: <one-line description of what changed>\" "
            f"Do NOT close the issue. Only the reviewer may close it, after independently "
            f"re-fetching the Japanese sources and verifying your fix."
        )
        ok = run_claude_fresh(author_prompt, model=AUTHOR_MODEL, effort=AUTHOR_EFFORT)
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
        ok = run_claude_fresh(re_reviewer_prompt, model=REVIEWER_MODEL, effort=REVIEWER_EFFORT)
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

        approved = False
        snapshot = guide_file.read_text()
        try:
            structural_passed = structural_review_route(slug, route_id, route_title)
            if not structural_passed:
                log(f"{slug}/{route_id}: structural review did not pass — skipping accuracy review")
                continue

            if review_route(slug, route_id, route_title):
                approved = mark_route_reviewed(guide_file, slug, route_id, route_title)
            if approved:
                run_deploy()
            else:
                log(f"{slug}/{route_id}: did not pass — will retry next cycle")
        finally:
            # A reviewer can write approval before its CLI fails or GitHub becomes
            # unavailable. Never leave that optimistic flag for the next run to skip.
            if not approved:
                try:
                    latest = json.loads(guide_file.read_text())
                    if not isinstance(latest, dict) or not isinstance(latest.get("routes"), list):
                        raise ValueError("Invalid guide metadata")
                except (OSError, ValueError):
                    latest = json.loads(snapshot)
                for entry in latest.get("routes", []):
                    if entry["id"] == route_id:
                        entry["reviewed"] = False
                guide_file.write_text(json.dumps(latest, ensure_ascii=False, indent=2))


def run() -> None:
    if not agent_runner.credentials_available():
        err(f"No {agent_runner.provider()} credentials found — skipping review")
        return

    if not GAMES_JSON.exists():
        log("games.json not found, skipping")
        return

    if subprocess.run(["gh", "--version"], capture_output=True).returncode != 0:
        err("gh CLI not found — skipping review pass (install GitHub CLI to enable automated review)")
        return

    games = json.loads(GAMES_JSON.read_text())

    # GUIDE_REVIEW_VID scopes the review loop to one game (separate from GUIDE_PRIORITY_VID
    # which controls the guide-gen exit gate in entrypoint.sh).
    priority_vid = os.environ.get("GUIDE_REVIEW_VID") or os.environ.get("GUIDE_PRIORITY_VID")
    priority_route = os.environ.get("GUIDE_REVIEW_ROUTE")

    if priority_vid:
        log(f"GUIDE_REVIEW_VID={priority_vid}: scoping review to this game only")
    if priority_route:
        log(f"GUIDE_REVIEW_ROUTE={priority_route}: scoping review to this route only")

    reviewed_any = False

    for vid, entry in games.items():
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

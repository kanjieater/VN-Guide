"""
Automated VN guide review loop.
Runs after guide_gen.py. For each game that has guides but unreviewed routes:
  For each unreviewed route:
    Round loop (max MAX_REVIEW_ROUNDS):
      1. If the current work has an open PR, use marked PR comments as the review ledger
      2. Otherwise fall back to one blocking issue per route/review type
      3. Run author/reviewer correction rounds against that destination
      4. Mark reviewed only after both structural and accuracy gates are clean
  Each route is reviewed in its own fresh claude session — never batched.

GUIDE_PRIORITY_VID: only process this game (same env var as guide_gen.py).
GUIDE_REVIEW_ROUTE: only process this route id within the priority game (for testing).

Author and reviewer are always separate claude invocations with no shared session.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_PATH = Path(os.environ.get("REPO_PATH", "/app/repo"))
SCRIPTS_PATH = Path(__file__).parent
GAMES_JSON = REPO_PATH / "games.json"

REVIEWER_MODEL = os.environ.get("GUIDE_REVIEWER_MODEL", "claude-sonnet-5")
REVIEWER_EFFORT = os.environ.get("GUIDE_REVIEWER_EFFORT", "max")
STRUCTURAL_REVIEWER_MODEL = os.environ.get("GUIDE_STRUCTURAL_REVIEWER_MODEL", "claude-sonnet-5")
STRUCTURAL_REVIEWER_EFFORT = os.environ.get("GUIDE_STRUCTURAL_REVIEWER_EFFORT", "high")
AUTHOR_MODEL = os.environ.get("GUIDE_AUTHOR_MODEL", "claude-sonnet-5")
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


_repo_full_name_cache: str | None = None
_open_pr_cache: int | None | bool = False


def get_repo_full_name() -> str | None:
    """Return owner/name for the current repository."""
    global _repo_full_name_cache
    if _repo_full_name_cache is not None:
        return _repo_full_name_cache
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err(f"Could not resolve repository name: {result.stderr.strip()}")
        return None
    value = result.stdout.strip()
    if value:
        _repo_full_name_cache = value
    return value or None


def get_open_pr_number() -> int | None:
    """Return the open PR for the current work, if one exists.

    GUIDE_REVIEW_PR may explicitly bind automated review to a PR. Otherwise the
    current git branch is matched against open PR heads. No PR means issue
    fallback mode.
    """
    global _open_pr_cache
    if _open_pr_cache is not False:
        return _open_pr_cache if isinstance(_open_pr_cache, int) else None

    override = os.environ.get("GUIDE_REVIEW_PR")
    if override:
        try:
            _open_pr_cache = int(override)
            return _open_pr_cache
        except ValueError:
            err(f"Invalid GUIDE_REVIEW_PR={override!r}; ignoring")

    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
    if not branch:
        _open_pr_cache = None
        return None

    result = subprocess.run(
        ["gh", "pr", "list",
         "--head", branch,
         "--state", "open",
         "--limit", "1",
         "--json", "number"],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err(f"gh pr list failed: {result.stderr.strip()}")
        _open_pr_cache = None
        return None
    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        rows = []
    _open_pr_cache = int(rows[0]["number"]) if rows else None
    return _open_pr_cache if isinstance(_open_pr_cache, int) else None


def pr_review_marker(review_type: str, slug: str, route_id: str) -> str:
    return f"<!-- vn-guide-review:{review_type}:{slug}:{route_id} -->"


def pr_fix_marker(review_type: str, slug: str, route_id: str) -> str:
    return f"<!-- vn-guide-fix:{review_type}:{slug}:{route_id} -->"


def pr_invalidate_marker(review_type: str, slug: str, route_id: str) -> str:
    return f"<!-- vn-guide-invalidate:{review_type}:{slug}:{route_id} -->"


def get_pr_review_status(
    pr_number: int, review_type: str, slug: str, route_id: str
) -> str | None:
    """Return the latest marked PR review status for a route/type."""
    repo_name = get_repo_full_name()
    if not repo_name:
        return None
    endpoint = f"repos/{repo_name}/issues/{pr_number}/comments?per_page=100"
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", endpoint],
        capture_output=True, text=True, cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err(f"Could not read PR #{pr_number} review ledger: {result.stderr.strip()}")
        return None
    try:
        pages = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return None

    comments = []
    if pages and isinstance(pages[0], list):
        for page in pages:
            comments.extend(page)
    elif isinstance(pages, list):
        comments = pages

    marker = pr_review_marker(review_type, slug, route_id)
    invalidation_marker = pr_invalidate_marker(review_type, slug, route_id)
    matches = [c for c in comments if marker in (c.get("body") or "")]
    if not matches:
        return None

    latest = max(matches, key=lambda item: item.get("id", 0))
    invalidations = [
        c for c in comments
        if invalidation_marker in (c.get("body") or "")
    ]
    if invalidations:
        latest_invalidation = max(
            invalidations, key=lambda item: item.get("id", 0)
        )
        if latest_invalidation.get("id", 0) > latest.get("id", 0):
            return None

    body = latest.get("body") or ""
    match = re.search(
        r"(?im)^\s*Status:\s*(PASS|CHANGES_REQUESTED|RESOLVED)\s*$",
        body,
    )
    return match.group(1).upper() if match else None


def pr_initial_review_prompt(
    pr_number: int, review_type: str, slug: str, route_id: str
) -> str:
    marker = pr_review_marker(review_type, slug, route_id)
    return (
        f"An open PR #{pr_number} exists for this work. Use that PR as the review ledger; "
        f"do not create a route review issue. Post one top-level PR comment beginning with "
        f"the exact marker `{marker}`. On the next line write exactly 'Status: PASS' if clean or "
        f"'Status: CHANGES_REQUESTED' if findings exist, followed by the findings. "
        f"Before posting, check the PR for an existing comment with the same marker and "
        f"do not race another {review_type} reviewer for this route. "
    )


def pr_author_fix_prompt(
    pr_number: int, review_type: str, slug: str, route_id: str
) -> str:
    review_marker = pr_review_marker(review_type, slug, route_id)
    fix_marker = pr_fix_marker(review_type, slug, route_id)
    return (
        f"Review is tracked on PR #{pr_number}. Read the latest PR comment containing "
        f"{review_marker!r} with Status: CHANGES_REQUESTED and apply every requested fix. "
        f"When done, post a top-level PR comment beginning with {fix_marker!r}, followed by "
        f"'Fixed: <concise summary>'. Do not post PASS/RESOLVED and do not create or close "
        f"a route review issue. "
    )


def pr_rereview_prompt(
    pr_number: int, review_type: str, slug: str, route_id: str
) -> str:
    marker = pr_review_marker(review_type, slug, route_id)
    fix_marker = pr_fix_marker(review_type, slug, route_id)
    return (
        f"Re-review is tracked on PR #{pr_number}. Read the latest CHANGES_REQUESTED review "
        f"with marker `{marker}` and the author's latest fix comment with marker "
        f"`{fix_marker}`. Post a new top-level PR comment beginning with the same "
        f"review marker. Write exactly 'Status: RESOLVED' if every "
        f"finding is fixed, otherwise 'Status: CHANGES_REQUESTED' and describe what remains. "
        f"Do not create a route review issue. "
    )


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
        err(f"gh issue list (structural) failed: {result.stderr.strip()}")
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


def structural_review_route_pr(
    pr_number: int, slug: str, route_id: str, route_title: str
) -> bool:
    """Run structural review using the open PR as the review ledger."""
    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(
            f"Route {route_id}: structural PR review round "
            f"{round_num}/{MAX_REVIEW_ROUNDS}"
        )
        status = get_pr_review_status(
            pr_number, "structural", slug, route_id
        )
        if status in {"PASS", "RESOLVED"}:
            log(f"Route {route_id}: structural PR review is {status}")
            return True

        if status is None:
            reviewer_prompt = (
                f"Read .claude/guide-standards.md and "
                f".claude/agents/guide-reviewer-structural.md and follow them exactly. "
                f"Review the structure of the '{route_title}' route for '{slug}'. "
                f"The route file is {slug}/route_{route_id}.json. "
                f"Do NOT fetch Japanese walkthroughs. Trace the main route and every "
                f"bad-end chain. "
                + pr_initial_review_prompt(
                    pr_number, "structural", slug, route_id
                )
            )
            ok = run_claude_fresh(
                reviewer_prompt,
                model=STRUCTURAL_REVIEWER_MODEL,
                effort=STRUCTURAL_REVIEWER_EFFORT,
            )
            if not ok:
                err(f"Structural reviewer failed for {slug}/{route_id}")
                return False
            status = get_pr_review_status(
                pr_number, "structural", slug, route_id
            )
            if status in {"PASS", "RESOLVED"}:
                return True
            if status != "CHANGES_REQUESTED":
                err(
                    f"Structural reviewer did not leave a valid PR status for "
                    f"{slug}/{route_id}"
                )
                return False

        if round_num == MAX_REVIEW_ROUNDS:
            log(
                f"Route {route_id}: structural PR review reached max rounds — "
                f"manual review needed"
            )
            return False

        author_prompt = (
            f"Read .claude/guide-standards.md and "
            f".claude/agents/guide-author.md and follow them exactly. "
            f"Fix structural findings for the '{route_title}' route in '{slug}'. "
            f"Apply fixes to {slug}/route_{route_id}.json. "
            + pr_author_fix_prompt(
                pr_number, "structural", slug, route_id
            )
        )
        ok = run_claude_fresh(
            author_prompt, model=AUTHOR_MODEL, effort=AUTHOR_EFFORT
        )
        if not ok:
            err(f"Author failed structural fix for {slug}/{route_id}")
            return False
        run_deploy()

        rereviewer_prompt = (
            f"Read .claude/guide-standards.md and "
            f".claude/agents/guide-reviewer-structural.md and follow them exactly. "
            f"Re-review the structure of the '{route_title}' route for '{slug}'. "
            f"Re-read {slug}/route_{route_id}.json and re-trace all bad-end chains. "
            + pr_rereview_prompt(
                pr_number, "structural", slug, route_id
            )
        )
        ok = run_claude_fresh(
            rereviewer_prompt,
            model=STRUCTURAL_REVIEWER_MODEL,
            effort=STRUCTURAL_REVIEWER_EFFORT,
        )
        if not ok:
            err(f"Structural re-reviewer failed for {slug}/{route_id}")
            return False

        status = get_pr_review_status(
            pr_number, "structural", slug, route_id
        )
        if status == "RESOLVED":
            return True
        if status != "CHANGES_REQUESTED":
            err(
                f"Structural re-review did not leave a valid PR status for "
                f"{slug}/{route_id}"
            )
            return False

    return False


def structural_review_route(slug: str, route_id: str, route_title: str) -> bool:
    """Run structural review; prefer an open PR, otherwise use issue fallback."""
    pr_number = get_open_pr_number()
    if pr_number is not None:
        return structural_review_route_pr(
            pr_number, slug, route_id, route_title
        )

    guide_file = REPO_PATH / slug / "guide.json"

    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(f"Route {route_id}: structural round {round_num}/{MAX_REVIEW_ROUNDS}")

        existing_issue = get_open_structural_issue_for_route(slug, route_id, route_title)

        if existing_issue is None:
            log(f"Route {route_id}: no open structural issue — running structural reviewer")
            reviewer_prompt = (
                f"Read .claude/guide-standards.md and .claude/agents/guide-reviewer-structural.md and follow them exactly. "
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
            f"Read .claude/guide-standards.md and .claude/agents/guide-author.md and follow them exactly. "
            f"Fix GitHub issue #{existing_issue} for the '{route_title}' route in '{slug}'. "
            f"First read the issue: gh issue view {existing_issue} "
            f"Apply all required structural fixes to {slug}/route_{route_id}.json. "
            f"When done, report what you changed: "
            f"gh issue comment {existing_issue} --body \"Fixed: <one-line description of what changed>\" "
            f"Do NOT close the issue. Only the reviewer may close it, after independently "
            f"verifying the structural fix."
        )
        ok = run_claude_fresh(author_prompt, model=AUTHOR_MODEL, effort=AUTHOR_EFFORT)
        if not ok:
            err(f"Author failed for structural fix {slug}/{route_id} round {round_num}")
            return False

        run_deploy()

        log(f"Route {route_id}: re-reviewing structure after author corrections (round {round_num})")
        re_reviewer_prompt = (
            f"Read .claude/guide-standards.md and .claude/agents/guide-reviewer-structural.md and follow them exactly. "
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


def review_route_pr(
    pr_number: int, slug: str, route_id: str, route_title: str
) -> bool:
    """Run accuracy review using the open PR as the review ledger."""
    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(
            f"Route {route_id}: accuracy PR review round "
            f"{round_num}/{MAX_REVIEW_ROUNDS}"
        )
        status = get_pr_review_status(
            pr_number, "accuracy", slug, route_id
        )
        if status in {"PASS", "RESOLVED"}:
            log(f"Route {route_id}: accuracy PR review is {status}")
            return True

        if status is None:
            reviewer_prompt = (
                f"Read .claude/guide-standards.md and "
                f".claude/agents/guide-reviewer.md and follow them exactly. "
                f"Review the '{route_title}' route for '{slug}'. "
                f"The route file is {slug}/route_{route_id}.json. "
                f"Fetch both Japanese verification sets documented in "
                f"{slug}/research.json and independently verify the route. "
                + pr_initial_review_prompt(
                    pr_number, "accuracy", slug, route_id
                )
            )
            ok = run_claude_fresh(
                reviewer_prompt,
                model=REVIEWER_MODEL,
                effort=REVIEWER_EFFORT,
            )
            if not ok:
                err(f"Accuracy reviewer failed for {slug}/{route_id}")
                return False
            status = get_pr_review_status(
                pr_number, "accuracy", slug, route_id
            )
            if status in {"PASS", "RESOLVED"}:
                return True
            if status != "CHANGES_REQUESTED":
                err(
                    f"Accuracy reviewer did not leave a valid PR status for "
                    f"{slug}/{route_id}"
                )
                return False

        if round_num == MAX_REVIEW_ROUNDS:
            log(
                f"Route {route_id}: accuracy PR review reached max rounds — "
                f"manual review needed"
            )
            return False

        author_prompt = (
            f"Read .claude/guide-standards.md and "
            f".claude/agents/guide-author.md and follow them exactly. "
            f"Fix accuracy findings for the '{route_title}' route in '{slug}'. "
            f"Apply required fixes to {slug}/route_{route_id}.json. "
            + pr_author_fix_prompt(
                pr_number, "accuracy", slug, route_id
            )
        )
        ok = run_claude_fresh(
            author_prompt, model=AUTHOR_MODEL, effort=AUTHOR_EFFORT
        )
        if not ok:
            err(f"Author failed accuracy fix for {slug}/{route_id}")
            return False
        run_deploy()

        rereviewer_prompt = (
            f"Read .claude/guide-standards.md and "
            f".claude/agents/guide-reviewer.md and follow them exactly. "
            f"Re-review the '{route_title}' route for '{slug}' after corrections. "
            f"Re-fetch the relevant components of both Japanese verification sets "
            f"documented in {slug}/research.json and verify every finding. "
            + pr_rereview_prompt(
                pr_number, "accuracy", slug, route_id
            )
        )
        ok = run_claude_fresh(
            rereviewer_prompt,
            model=REVIEWER_MODEL,
            effort=REVIEWER_EFFORT,
        )
        if not ok:
            err(f"Accuracy re-reviewer failed for {slug}/{route_id}")
            return False

        status = get_pr_review_status(
            pr_number, "accuracy", slug, route_id
        )
        if status == "RESOLVED":
            return True
        if status != "CHANGES_REQUESTED":
            err(
                f"Accuracy re-review did not leave a valid PR status for "
                f"{slug}/{route_id}"
            )
            return False

    return False


def mark_route_reviewed(guide_file: Path, slug: str, route_id: str, route_title: str) -> bool:
    """Set reviewed: true only when both review gates have no open blocker.

    Re-check here rather than trusting caller state: a reviewer can file a fresh
    issue during the same round that otherwise appeared to pass.
    """
    pr_number = get_open_pr_number()
    if pr_number is not None:
        structural_status = get_pr_review_status(
            pr_number, "structural", slug, route_id
        )
        accuracy_status = get_pr_review_status(
            pr_number, "accuracy", slug, route_id
        )
        clean = {"PASS", "RESOLVED"}
        if structural_status not in clean:
            err(
                f"Refusing to mark {slug}/{route_id} reviewed — "
                f"structural PR status is {structural_status!r}"
            )
            return False
        if accuracy_status not in clean:
            err(
                f"Refusing to mark {slug}/{route_id} reviewed — "
                f"accuracy PR status is {accuracy_status!r}"
            )
            return False

        legacy_accuracy = get_open_issue_for_route(
            slug, route_id, route_title
        )
        legacy_structural = get_open_structural_issue_for_route(
            slug, route_id, route_title
        )
        if legacy_accuracy is not None or legacy_structural is not None:
            err(
                f"Refusing to mark {slug}/{route_id} reviewed — "
                f"legacy review issue still open "
                f"(accuracy={legacy_accuracy}, structural={legacy_structural})"
            )
            return False
    else:
        accuracy_blocking = get_open_issue_for_route(
            slug, route_id, route_title
        )
        if accuracy_blocking is not None:
            err(
                f"Refusing to mark {slug}/{route_id} reviewed — "
                f"accuracy issue #{accuracy_blocking} is still open"
            )
            return False

        structural_blocking = get_open_structural_issue_for_route(
            slug, route_id, route_title
        )
        if structural_blocking is not None:
            err(
                f"Refusing to mark {slug}/{route_id} reviewed — "
                f"structural issue #{structural_blocking} is still open"
            )
            return False

    guide = json.loads(guide_file.read_text())
    for route in guide.get("routes", []):
        if route["id"] == route_id:
            route["reviewed"] = True
    guide_file.write_text(json.dumps(guide, ensure_ascii=False, indent=2))
    log(f"Route {route_id} marked reviewed in {guide_file.relative_to(REPO_PATH)}")
    return True


def review_route(slug: str, route_id: str, route_title: str) -> bool:
    """Run accuracy review; prefer an open PR, otherwise use issue fallback."""
    pr_number = get_open_pr_number()
    if pr_number is not None:
        return review_route_pr(pr_number, slug, route_id, route_title)

    guide_file = REPO_PATH / slug / "guide.json"

    for round_num in range(1, MAX_REVIEW_ROUNDS + 1):
        log(f"Route {route_id}: round {round_num}/{MAX_REVIEW_ROUNDS}")

        existing_issue = get_open_issue_for_route(slug, route_id, route_title)

        if existing_issue is None:
            # No open issue — run fresh reviewer for this route
            log(f"Route {route_id}: no open issue — running reviewer")
            reviewer_prompt = (
                f"Read .claude/guide-standards.md and .claude/agents/guide-reviewer.md and follow them exactly. "
                f"Review the '{route_title}' route for the game '{slug}'. "
                f"The route file is {slug}/route_{route_id}.json. "
                f"Fetch both Japanese verification sets documented in {slug}/research.json. "
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
            f"Read .claude/guide-standards.md and .claude/agents/guide-author.md and follow them exactly. "
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
            f"Read .claude/guide-standards.md and .claude/agents/guide-reviewer.md and follow them exactly. "
            f"Re-review the '{route_title}' route for '{slug}' after author corrections. "
            f"First read the existing issue: gh issue view {existing_issue} "
            f"Re-fetch the relevant components of both Japanese verification sets documented in {slug}/research.json. "
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

        structural_passed = structural_review_route(slug, route_id, route_title)
        if not structural_passed:
            log(f"{slug}/{route_id}: structural review did not pass — skipping accuracy review")
            continue

        passed = review_route(slug, route_id, route_title)
        if passed:
            if mark_route_reviewed(guide_file, slug, route_id, route_title):
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

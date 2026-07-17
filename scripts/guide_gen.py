"""
Automated VN guide generation using Claude CLI.
Runs after generate.py. For each game with has_guide=false, runs Claude in phases:
  Phase 1 – Research (one call): finds Japanese guides, determines route order → research.json
  Phase 2 – Per route (one call each): generates steps → route_{id}.json
             After each route: assemble guide.json and deploy so it's visible immediately
  Phase 3 – Final cleanup: remove intermediate route_*.json files

Intermediate files survive container restarts so generation resumes where it left off.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import generate as _generate

REPO_PATH = Path(os.environ.get("REPO_PATH", "/app/repo"))
SCRIPTS_PATH = Path(__file__).parent
PROMPTS_PATH = SCRIPTS_PATH / "prompts"
GAMES_JSON = REPO_PATH / "games.json"

MODEL = os.environ.get("GUIDE_GEN_MODEL", "claude-sonnet-5")
MAX_TURNS_RESEARCH = 30
MAX_TURNS_ROUTE = 35


def log(msg: str) -> None:
    print(f"[guide_gen] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[guide_gen] {msg}", file=sys.stderr, flush=True)


def find_latest_session(cwd: Path) -> str | None:
    """Find the most recent Claude session ID for the given working directory.

    Claude stores sessions at ~/.claude/projects/<encoded-cwd>/<session-id>.jsonl
    where encoded-cwd is the absolute path with '/' replaced by '-'.
    """
    projects_dir = Path.home() / ".claude" / "projects"
    encoded = str(cwd).replace("/", "-")
    project_dir = projects_dir / encoded
    if not project_dir.exists():
        return None
    sessions = sorted(project_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return sessions[-1].stem if sessions else None


def run_claude(prompt: str, max_turns: int, cwd: Path,
               session_file: Path | None = None) -> bool:
    """Invoke claude CLI in non-interactive mode. Output streams to Docker logs.

    If session_file exists and contains a session ID, resumes that session with
    a short continuation prompt instead of the full prompt — avoids re-spending
    tokens on work already done when a previous run hit a rate limit mid-task.
    Saves the session ID to session_file after every run so the next attempt
    can resume.
    """
    session_id = session_file.read_text().strip() if session_file and session_file.exists() else None

    if session_id:
        log(f"Resuming session {session_id}")
        cmd = [
            "claude",
            "--resume", session_id,
            "-p", "The previous session was interrupted. Continue where you left off "
                  "and write the output file as soon as you have enough information.",
            "--dangerously-skip-permissions",
            "--model", MODEL,
            "--max-turns", str(max_turns),
        ]
    else:
        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--model", MODEL,
            "--max-turns", str(max_turns),
        ]

    try:
        result = subprocess.run(cmd, cwd=str(cwd), timeout=900)
        ok = result.returncode == 0
    except subprocess.TimeoutExpired:
        err("Claude timed out after 900s")
        ok = False
    except FileNotFoundError:
        err("claude CLI not found — is @anthropic-ai/claude-code installed?")
        return False

    if session_file is not None:
        sid = find_latest_session(cwd)
        if sid:
            session_file.write_text(sid)

    return ok


def run_deploy() -> None:
    """Commit and push whatever changed. Push failure is non-fatal."""
    result = subprocess.run(
        ["python3", str(SCRIPTS_PATH / "deploy.py")],
        cwd=str(REPO_PATH),
    )
    if result.returncode != 0:
        err("Deploy failed — guide saved locally, will push on next cycle")


def build_prompt(template_name: str, **kwargs) -> str:
    tmpl = (PROMPTS_PATH / template_name).read_text()
    prompt_md = (REPO_PATH / "prompt.md").read_text()
    tmpl = tmpl.replace("$PROMPT_MD", prompt_md)
    # Longest keys first so $SAVE_OFFSET_PLUS1 is replaced before $SAVE_OFFSET
    for key, val in sorted(kwargs.items(), key=lambda x: -len(x[0])):
        tmpl = tmpl.replace(f"${key}", str(val))
    return tmpl


def load_completed_routes(routes: list[dict], guide_dir: Path) -> list[dict]:
    """Return route dicts with steps for every route that has a completed JSON file."""
    result = []
    for route in routes:
        route_id = route["id"]
        route_file = guide_dir / f"route_{route_id}.json"
        if not route_file.exists():
            continue
        try:
            steps = json.loads(route_file.read_text())
            if isinstance(steps, list):
                result.append({
                    "id": route_id,
                    "title": route.get("title", route_id),
                    "steps": steps,
                })
        except json.JSONDecodeError:
            pass
    return result


def assemble(slug: str, title: str, vndb_id: str, completed_routes: list[dict],
             guide_dir: Path, research: dict) -> None:
    """Write guide.json with metadata + route list (no steps — steps live in route_{id}.json).

    The HTML fetches route_{id}.json lazily when a route is selected.
    stepCount is included so the home screen can show progress % without loading steps.
    """
    research_routes = {r["id"]: r for r in research.get("routes", [])}

    # Preserve any portrait data already in guide.json (agent may have set it manually)
    existing_portraits: dict[str, str] = {}
    existing_guide = guide_dir / "guide.json"
    if existing_guide.exists():
        try:
            existing = json.loads(existing_guide.read_text())
            for r in existing.get("routes", []):
                if r.get("portrait"):
                    existing_portraits[r["id"]] = r["portrait"]
        except (json.JSONDecodeError, KeyError):
            pass

    route_list = []
    for r in completed_routes:
        entry: dict = {
            "id": r["id"],
            "title": r["title"],
            "stepCount": len(r["steps"]),
        }
        portrait = (research_routes.get(r["id"], {}).get("portrait", "")
                    or existing_portraits.get(r["id"], ""))
        if portrait:
            entry["portrait"] = portrait
        route_list.append(entry)

    guide_data = {
        "title": title,
        "vndb_id": vndb_id,
        "routes": route_list,
        "sources": research.get("sources", []),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (guide_dir / "guide.json").write_text(
        json.dumps(guide_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    total = len(research.get("routes", []))
    log(f"Updated guide.json ({len(route_list)}/{total} routes)")


def phase_research(slug: str, title: str, vndb_id: str, guide_dir: Path) -> bool:
    research_file = guide_dir / "research.json"
    if research_file.exists():
        log(f"Research already done for {slug}, skipping")
        return True

    log(f"Phase 1 – Research: {title}")
    prompt = build_prompt(
        "research.md",
        TITLE=title,
        VNDB_ID=vndb_id,
        RESEARCH_FILE=str(research_file),
        DATE=datetime.now(timezone.utc).isoformat(),
    )
    session_file = guide_dir / "research_session.txt"
    ok = run_claude(prompt, MAX_TURNS_RESEARCH, guide_dir, session_file=session_file)

    if not ok or not research_file.exists():
        err(f"Research phase failed for {slug}")
        return False

    session_file.unlink(missing_ok=True)

    try:
        data = json.loads(research_file.read_text())
        if not data.get("routes"):
            err(f"research.json has no routes for {slug}")
            return False
        log(f"Research complete: {len(data['routes'])} routes found")
        return True
    except json.JSONDecodeError as e:
        err(f"research.json is invalid JSON: {e}")
        return False


def count_saves_in_route(route_file: Path) -> int:
    """Count セーブN steps in a completed route file."""
    try:
        steps = json.loads(route_file.read_text())
        return sum(1 for s in steps if isinstance(s.get("simpleJp", ""), str) and s["simpleJp"].startswith("セーブ"))
    except Exception:
        return 0


def compute_save_offset(routes: list, route_idx: int, guide_dir: Path) -> int:
    """Total saves in all routes before route_idx (for cross-route slot numbering)."""
    total = 0
    for i, r in enumerate(routes):
        if i >= route_idx:
            break
        total += count_saves_in_route(guide_dir / f"route_{r['id']}.json")
    return total


def generate_guide(slug: str, title: str, vndb_id: str, max_routes: int | None = None) -> bool:
    guide_dir = REPO_PATH / slug
    guide_dir.mkdir(exist_ok=True)

    if not phase_research(slug, title, vndb_id, guide_dir):
        return False

    research = json.loads((guide_dir / "research.json").read_text())
    routes = research.get("routes", [])

    for i, route in enumerate(routes):
        if max_routes is not None and i >= max_routes:
            log(f"Reached max_routes={max_routes}, stopping")
            break

        route_id = route["id"]
        route_file = guide_dir / f"route_{route_id}.json"

        if route_file.exists():
            log(f"Route {route_id} already done, skipping")
        else:
            save_offset = compute_save_offset(routes, i, guide_dir)
            log(f"Phase 2 – Route: {route.get('title', route_id)} (save offset: {save_offset})")
            prompt = build_prompt(
                "route.md",
                TITLE=title,
                VNDB_ID=vndb_id,
                ROUTE_ID=route_id,
                ROUTE_TITLE=route.get("title", route_id),
                RESEARCH_FILE=str(guide_dir / "research.json"),
                ROUTE_FILE=str(route_file),
                SAVE_OFFSET=str(save_offset),
                SAVE_OFFSET_PLUS1=str(save_offset + 1),
            )
            route_session_file = guide_dir / f"route_{route_id}_session.txt"
            ok = run_claude(prompt, MAX_TURNS_ROUTE, guide_dir, session_file=route_session_file)

            if not ok or not route_file.exists():
                err(f"Route {route_id} failed for {slug}")
                return False

            route_session_file.unlink(missing_ok=True)

            try:
                steps = json.loads(route_file.read_text())
                if not isinstance(steps, list):
                    err(f"route_{route_id}.json is not a JSON array")
                    return False
                log(f"Route {route_id} done: {len(steps)} steps")
            except json.JSONDecodeError as e:
                err(f"route_{route_id}.json is invalid JSON: {e}")
                return False

        # Assemble and deploy after every completed route so it's visible immediately
        completed = load_completed_routes(routes, guide_dir)
        assemble(slug, title, vndb_id, completed, guide_dir, research)
        run_deploy()

    return True


def run() -> None:
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_oauth = Path.home().joinpath(".claude", ".credentials.json").exists()
    if not has_api_key and not has_oauth:
        log("No Anthropic credentials found — skipping guide generation")
        return

    if not GAMES_JSON.exists():
        log("games.json not found, skipping")
        return

    games = json.loads(GAMES_JSON.read_text())

    pending = [
        (vid, entry)
        for vid, entry in games.items()
        if not entry.get("has_guide", False)
    ]

    if not pending:
        log("All games have guides, nothing to do")
        return

    log(f"{len(pending)} game(s) need guides")

    vid, entry = pending[0]
    slug = entry["slug"]
    title = entry.get("title", slug)

    max_routes_env = os.environ.get("GUIDE_MAX_ROUTES")
    max_routes = int(max_routes_env) if max_routes_env else None
    if max_routes is not None:
        log(f"GUIDE_MAX_ROUTES={max_routes}: will stop after {max_routes} route(s)")

    success = generate_guide(slug, title, vid, max_routes=max_routes)

    if success:
        if max_routes is None:
            games[vid]["has_guide"] = True
            GAMES_JSON.write_text(json.dumps(games, ensure_ascii=False, indent=2) + "\n")
            log(f"Guide complete: {slug}")
            _generate.generate_landing(games)
            log("Regenerated landing page with updated has_guide status")
            run_deploy()
        else:
            log(f"Partial run ({max_routes} route(s)) done for {slug} — has_guide not flipped")
    else:
        err(f"Guide generation failed for {slug} — will retry next cycle")


if __name__ == "__main__":
    run()

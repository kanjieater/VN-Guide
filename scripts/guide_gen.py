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


def run_claude(prompt: str, max_turns: int, cwd: Path) -> bool:
    """Invoke claude CLI in non-interactive mode. Output streams to Docker logs."""
    try:
        result = subprocess.run(
            [
                "claude",
                "-p", prompt,
                "--dangerously-skip-permissions",
                "--model", MODEL,
                "--max-turns", str(max_turns),
            ],
            cwd=str(cwd),
            timeout=900,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        err("Claude timed out after 900s")
        return False
    except FileNotFoundError:
        err("claude CLI not found — is @anthropic-ai/claude-code installed?")
        return False


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
    for key, val in kwargs.items():
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
    route_list = [
        {
            "id": r["id"],
            "title": r["title"],
            "stepCount": len(r["steps"]),
        }
        for r in completed_routes
    ]
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
    ok = run_claude(prompt, MAX_TURNS_RESEARCH, guide_dir)

    if not ok or not research_file.exists():
        err(f"Research phase failed for {slug}")
        return False

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


def generate_guide(slug: str, title: str, vndb_id: str) -> bool:
    guide_dir = REPO_PATH / slug
    guide_dir.mkdir(exist_ok=True)

    if not phase_research(slug, title, vndb_id, guide_dir):
        return False

    research = json.loads((guide_dir / "research.json").read_text())
    routes = research.get("routes", [])

    for route in routes:
        route_id = route["id"]
        route_file = guide_dir / f"route_{route_id}.json"

        if route_file.exists():
            log(f"Route {route_id} already done, skipping")
        else:
            log(f"Phase 2 – Route: {route.get('title', route_id)}")
            prompt = build_prompt(
                "route.md",
                TITLE=title,
                VNDB_ID=vndb_id,
                ROUTE_ID=route_id,
                ROUTE_TITLE=route.get("title", route_id),
                RESEARCH_FILE=str(guide_dir / "research.json"),
                ROUTE_FILE=str(route_file),
            )
            ok = run_claude(prompt, MAX_TURNS_ROUTE, guide_dir)

            if not ok or not route_file.exists():
                err(f"Route {route_id} failed for {slug}")
                return False

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

    success = generate_guide(slug, title, vid)

    if success:
        games[vid]["has_guide"] = True
        GAMES_JSON.write_text(json.dumps(games, ensure_ascii=False, indent=2) + "\n")
        log(f"Guide complete: {slug}")
    else:
        err(f"Guide generation failed for {slug} — will retry next cycle")


if __name__ == "__main__":
    run()

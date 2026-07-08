"""
Automated VN guide generation using Claude CLI.
Runs after generate.py. For each game with has_guide=false, runs Claude in phases:
  Phase 1 – Research (one call): finds Japanese guides, determines route order → research.json
  Phase 2 – Per route (one call each): generates step JSON → route_{id}.json
  Phase 3 – Assembly (Python): combines route files into index.html, updates has_guide

Intermediate files (research.json, route_*.json) survive container restarts so
generation resumes where it left off if interrupted.
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
            timeout=900,  # 15 min ceiling per phase
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        err("Claude timed out after 900s")
        return False
    except FileNotFoundError:
        err("claude CLI not found — is @anthropic-ai/claude-code installed?")
        return False


def build_prompt(template_name: str, **kwargs) -> str:
    """Load a prompt template and substitute variables."""
    tmpl = (PROMPTS_PATH / template_name).read_text()
    prompt_md = (REPO_PATH / "prompt.md").read_text()
    tmpl = tmpl.replace("$PROMPT_MD", prompt_md)
    for key, val in kwargs.items():
        tmpl = tmpl.replace(f"${key}", str(val))
    return tmpl


def phase_research(slug: str, title: str, vndb_id: str, guide_dir: Path) -> bool:
    research_file = guide_dir / "research.json"
    if research_file.exists():
        log(f"Research already done for {slug}, skipping phase 1")
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

    # Validate JSON
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


def phase_routes(slug: str, title: str, vndb_id: str, guide_dir: Path) -> list[dict] | None:
    research_file = guide_dir / "research.json"
    research = json.loads(research_file.read_text())
    routes = research.get("routes", [])

    for route in routes:
        route_id = route["id"]
        route_file = guide_dir / f"route_{route_id}.json"

        if route_file.exists():
            log(f"Route {route_id} already done, skipping")
            continue

        log(f"Phase 2 – Route: {route.get('title', route_id)}")
        prompt = build_prompt(
            "route.md",
            TITLE=title,
            VNDB_ID=vndb_id,
            ROUTE_ID=route_id,
            ROUTE_TITLE=route.get("title", route_id),
            RESEARCH_FILE=str(research_file),
            ROUTE_FILE=str(route_file),
        )
        ok = run_claude(prompt, MAX_TURNS_ROUTE, guide_dir)

        if not ok or not route_file.exists():
            err(f"Route {route_id} failed for {slug}")
            return None

        # Validate JSON
        try:
            steps = json.loads(route_file.read_text())
            if not isinstance(steps, list):
                err(f"route_{route_id}.json is not a JSON array")
                return None
            log(f"Route {route_id} done: {len(steps)} steps")
        except json.JSONDecodeError as e:
            err(f"route_{route_id}.json is invalid JSON: {e}")
            return None

    # Return all routes with their steps loaded
    result = []
    for route in routes:
        route_id = route["id"]
        route_file = guide_dir / f"route_{route_id}.json"
        steps = json.loads(route_file.read_text())
        result.append({
            "id": route_id,
            "title": route.get("title", route_id),
            "steps": steps,
        })
    return result


def phase_assemble(slug: str, title: str, vndb_id: str, guide_routes: list[dict], guide_dir: Path, research: dict) -> bool:
    log(f"Phase 3 – Assembly: {slug} ({len(guide_routes)} routes)")

    guide_data = {
        "title": title,
        "vndb_id": vndb_id,
        "routes": guide_routes,
        "sources": research.get("sources", []),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (guide_dir / "guide.json").write_text(
        json.dumps(guide_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log(f"Wrote {slug}/guide.json")

    # Clean up intermediate route files (research.json is kept as source record)
    for route_file in guide_dir.glob("route_*.json"):
        route_file.unlink()
        log(f"Removed {route_file.name}")

    return True


def generate_guide(slug: str, title: str, vndb_id: str) -> bool:
    guide_dir = REPO_PATH / slug
    guide_dir.mkdir(exist_ok=True)

    if not phase_research(slug, title, vndb_id, guide_dir):
        return False

    research = json.loads((guide_dir / "research.json").read_text())

    guide_routes = phase_routes(slug, title, vndb_id, guide_dir)
    if guide_routes is None:
        return False

    return phase_assemble(slug, title, vndb_id, guide_routes, guide_dir, research)


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

    # Process one game per pipeline run to keep each run bounded
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

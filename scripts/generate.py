"""
Orchestrates the VN guide site generation:
  1. Load games.json from repo
  2. Fetch VNDB playing list
  3. Merge new games into games.json (with stable slugs)
  4. Scaffold <slug>/index.html for any new games
  5. Regenerate root index.html landing page
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pull_vndb

REPO_PATH = Path(os.environ.get("REPO_PATH", "/app/repo"))
SCRIPTS_PATH = Path(__file__).parent
TEMPLATES_PATH = SCRIPTS_PATH / "templates"

GAMES_JSON = REPO_PATH / "games.json"
LANDING_TMPL = TEMPLATES_PATH / "landing.html"
STUB_TMPL = TEMPLATES_PATH / "guide_stub.html"


# ── games.json ────────────────────────────────────────────────────────────────

def load_games() -> dict:
    if GAMES_JSON.exists():
        return json.loads(GAMES_JSON.read_text())
    return {}


def save_games(games: dict) -> None:
    GAMES_JSON.write_text(json.dumps(games, ensure_ascii=False, indent=2) + "\n")


def existing_slugs(games: dict) -> set[str]:
    return {v["slug"] for v in games.values()}


def make_slug(title: str, alttitle: str, vndb_id: str, used: set[str]) -> str:
    """Human-readable slug from title; fallback to vndb_id."""
    def slugify(s: str) -> str:
        s = s.lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_]+", "-", s).strip("-")
        return s

    # Prefer romanized title; try alttitle if it's ASCII-dominant
    candidates = [slugify(title)]
    if alttitle and re.search(r"[a-zA-Z]", alttitle):
        candidates.insert(0, slugify(alttitle))

    for candidate in candidates:
        if candidate and candidate not in used:
            return candidate

    # Collision or empty: use vndb_id
    base = vndb_id  # e.g. "v1629"
    slug = base
    n = 1
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    return slug


# ── Scaffold new guide dirs ───────────────────────────────────────────────────

def scaffold_guide(slug: str, title: str, vndb_id: str) -> None:
    guide_dir = REPO_PATH / slug
    guide_dir.mkdir(exist_ok=True)
    (guide_dir / "index.html").write_text(STUB_TMPL.read_text())
    guide_json = {"title": title, "vndb_id": vndb_id, "routes": []}
    (guide_dir / "guide.json").write_text(
        json.dumps(guide_json, ensure_ascii=False, indent=2)
    )
    manifest = {
        "name": f"{title} ガイド",
        "short_name": "VN Guide",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#121212",
        "theme_color": "#121212",
        "icons": [
            {"src": "../icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "../icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    (guide_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )
    print(f"[generate] Scaffolded guide: {slug}/")


# ── Landing page ──────────────────────────────────────────────────────────────

def generate_landing(games: dict) -> None:
    tmpl = LANDING_TMPL.read_text()

    game_list = [
        {
            "slug":      entry["slug"],
            "title":     entry.get("title", entry["slug"]),
            "alttitle":  entry.get("alttitle") or "",
            "has_guide": entry.get("has_guide", False),
            "cover_url": entry.get("cover_url") or "",
        }
        for entry in games.values()
    ]
    games_json = json.dumps(game_list, ensure_ascii=False)
    html = tmpl.replace("/* GAMES_DATA */", games_json)
    (REPO_PATH / "index.html").write_text(html)
    print(f"[generate] Wrote landing page ({len(games)} games)")


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    user = os.environ.get("VNDB_USER", "kanjieater")

    label = os.environ.get("VNDB_LABEL", "31")
    print(f"[generate] Fetching VNDB list (label {label}) for {user}")
    try:
        playing = pull_vndb.fetch_playing_list(user)
    except Exception as e:
        print(f"[generate] VNDB fetch failed: {e}", file=sys.stderr)
        playing = []

    games = load_games()
    used_slugs = existing_slugs(games)

    for vn in playing:
        vid = vn["vndb_id"]
        if vid in games:
            # Update mutable fields (cover may change, title may change)
            games[vid]["cover_url"] = vn["cover_url"]
            games[vid]["title"] = vn["title"]
            if vn["alttitle"]:
                games[vid]["alttitle"] = vn["alttitle"]
            continue

        # New game: assign stable slug
        slug = make_slug(vn["title"], vn["alttitle"], vid, used_slugs)
        used_slugs.add(slug)

        games[vid] = {
            "slug": slug,
            "has_guide": False,
            "title": vn["title"],
            "alttitle": vn["alttitle"],
            "cover_url": vn["cover_url"],
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        print(f"[generate] New game: {vn['title']} → {slug}/")

    # Back-fill cover URLs for any games.json entries that were added manually
    # (e.g. the initial YU-NO seed) and never got a cover from VNDB.
    for vid, entry in games.items():
        if not entry.get("cover_url"):
            vn = pull_vndb.lookup_vn_by_id(vid)
            if vn and vn.get("cover_url"):
                entry["cover_url"] = vn["cover_url"]
                print(f"[generate] Filled cover for {entry['title']}")

    # Scaffold directories for games that lack one
    for vid, entry in games.items():
        slug = entry["slug"]
        guide_dir = REPO_PATH / slug
        if not (guide_dir / "index.html").exists():
            scaffold_guide(slug, entry["title"], vid)

    save_games(games)
    generate_landing(games)


if __name__ == "__main__":
    run()

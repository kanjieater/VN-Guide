# Running a one-off container for a single game

Use this when you need Claude to generate (and review) the guide for exactly
one game, without touching any other game's guide or any other running
vn-guide container.

## 1. Pick a stopped/unused compose project to reuse (or make a new dir)

Check what's running first — never edit or restart a project that's `Up`:
```bash
docker compose ls
```
If nothing suitable is stopped, create a new directory under `/mnt/srv/`
with a `compose.yml` (copy an existing vn-guide-* project) and give it its
own `container_name`, `.env`, and its own named volume.

## 2. Find the VNDB id for the target game

```bash
python3 -c "import json; g=json.load(open('/home/ke/code/vn-guide/games.json'));
[print(k, v['slug'], v['has_guide']) for k,v in g.items()]"
```

## 3. Pin the container to that one game — required, not optional

In `.env`:
```
GUIDE_PRIORITY_VID=v405   # generate this game; container exits once has_guide=true
GUIDE_REVIEW_VID=v405     # review.py ONLY reviews this game's routes
GUIDE_WINDOW_DISABLE=1    # allow generation outside the normal 22:00-00:30 window
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0   # required — default 600s kills long route generations mid-run
```
**Without `GUIDE_REVIEW_VID`, `review.py` reviews every game with `has_guide: true`
in the whole repo** — it will run structural/accuracy reviews on other games'
routes owned by a different container. Always pin both.

## 4. Wire up Claude auth — do NOT bind-mount the whole ~/.claude dir

Share just the credentials file with the host, so token refreshes (on either
side) stay in sync instead of one side's copy going stale:

`compose.yml`:
```yaml
volumes:
  - /home/ke/code/vn-guide/scripts:/app/scripts
  - /home/ke/code/vn-guide:/app/repo
  - <some-claude-volume>:/home/guide/.claude
  - /home/ke/.claude/.credentials.json:/home/guide/.claude/.credentials.json
networks:
  - selfhost
```
Requires the host user to already be logged in via `claude` (a valid
`~/.claude/.credentials.json` with an active subscription).

## 5. Start it and verify it's actually doing work, not just up

```bash
cd /mnt/srv/<project-dir>
docker compose up -d --force-recreate
docker logs <container_name> --tail 20
```
Look for:
- `[refresh_oauth] Access token still valid...` — auth is fine
- `[guide_gen] Phase 2 – Route: ...` — it picked up the target game
- No `Failed to authenticate` / `Background tasks still running after 600s` / `Route ... failed`

"Up" in `docker compose ps` only means the container process is alive — it
does NOT mean generation is progressing. Confirm with a real `claude -p`
process inside the container:
```bash
docker exec <container_name> sh -c "cat /proc/*/cmdline 2>/dev/null | tr '\0' ' \n'" | grep claude
```
A single route can legitimately take many minutes (research + cross-validation
+ writing) — no output for a while isn't necessarily stuck; check the process
is still alive.

## 6. It shuts itself down when done

Once `GUIDE_PRIORITY_VID`'s game reaches `has_guide: true` in `games.json`,
the container exits on its own (checked after each pipeline cycle). It will
not automatically move on to the next pending game — that's intentional so it
never wanders into games it wasn't asked to touch.

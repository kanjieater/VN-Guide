import { test } from "bun:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { syncLandingIndex } from "../tools/sync-landing-index.mjs";

test("index-only sync discovers directories, is deterministic and never writes other files", async () => {
  const root = await mkdtemp(join(tmpdir(), "vn-index-"));
  try {
    await mkdir(join(root, "templates"));
    await writeFile(join(root, "games.json"), JSON.stringify({ v1: { slug: "old", title: "Old", has_guide: true } }));
    await writeFile(join(root, "templates", "landing.html"), "before /* GAMES_DATA */ after");
    await writeFile(join(root, "templates", "guide.html"), "shell");
    await mkdir(join(root, "new-game"));
    await writeFile(join(root, "new-game", "catalog.json"), JSON.stringify({ vndb_id: "v2", title: "New" }));
    await writeFile(join(root, "new-game", "guide.json"), JSON.stringify({ vndb_id: "v2", routes: [{ reviewed: false }] }));
    assert.equal(await syncLandingIndex(root), true);
    let html = await readFile(join(root, "index.html"), "utf8");
    assert.match(html, /New/);
    assert.match(html, /"has_guide":false/);
    assert.equal(await syncLandingIndex(root), false);
    await assert.rejects(syncLandingIndex(root, { check: true }), /out of sync/).catch(error => { throw error; });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

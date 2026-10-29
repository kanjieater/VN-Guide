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
    assert.equal(await syncLandingIndex(root, { check: true }), false);
    await writeFile(join(root, "new-game", "guide.json"), JSON.stringify({ vndb_id: "v2", routes: [{ reviewed: true }] }));
    await assert.rejects(syncLandingIndex(root, { check: true }), /out of sync/);
    assert.equal(await syncLandingIndex(root), true);
    html = await readFile(join(root, "index.html"), "utf8");
    assert.match(html, /"has_guide":true/);
    await assert.rejects(readFile(join(root, "new-game", "index.html"), "utf8"), { code: "ENOENT" });
    await assert.rejects(readFile(join(root, "new-game", "manifest.json"), "utf8"), { code: "ENOENT" });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("index sync creates a missing root index without changing game files", async () => {
  const root = await mkdtemp(join(tmpdir(), "vn-index-missing-"));
  try {
    await mkdir(join(root, "templates"));
    await writeFile(join(root, "games.json"), JSON.stringify({}));
    await writeFile(join(root, "templates", "landing.html"), "/* GAMES_DATA */");
    await writeFile(join(root, "templates", "guide.html"), "shell");
    assert.equal(await syncLandingIndex(root), true);
    assert.equal(await readFile(join(root, "index.html"), "utf8"), "[]");
    assert.equal(await syncLandingIndex(root), false);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

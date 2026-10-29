import { test } from "bun:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadCatalog } from "../tools/catalog.mjs";

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "vn-catalog-"));
  await writeFile(join(root, "games.json"), JSON.stringify({
    v1: { slug: "old", title: "Legacy", has_guide: true },
  }));
  return root;
}

async function game(root, slug, metadata, guide = { vndb_id: "v2", routes: [{ reviewed: true }] }) {
  await mkdir(join(root, slug), { recursive: true });
  await writeFile(join(root, slug, "catalog.json"), JSON.stringify(metadata));
  await writeFile(join(root, slug, "guide.json"), JSON.stringify(guide));
}

test("discovers new independent games without editing games.json", async () => {
  const root = await fixture();
  try {
    await game(root, "new-game", { vndb_id: "v2", title: "New", cover_url: "cover.jpg" });
    const entries = await loadCatalog(root);
    assert.equal(entries.v1.title, "Legacy");
    assert.deepEqual(entries.v2, { slug: "new-game", title: "New", cover_url: "cover.jpg", has_guide: true });
    await game(root, "pending", { vndb_id: "v3", slug: "pending", title: "Pending" },
      { vndb_id: "v3", routes: [{ reviewed: true }, { reviewed: false }] });
    assert.equal((await loadCatalog(root)).v3.has_guide, false);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("migrated legacy entries use per-game metadata as source of truth", async () => {
  const root = await fixture();
  try {
    await game(root, "old", { vndb_id: "v1", title: "Updated" },
      { vndb_id: "v1", routes: [{ reviewed: false }] });
    assert.deepEqual((await loadCatalog(root)).v1, { slug: "old", title: "Updated", has_guide: false });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("rejects conflicting or malformed per-game metadata", async () => {
  const cases = [
    [{ vndb_id: "v1", title: "Collision" }, { vndb_id: "v1", routes: [{ reviewed: true }] }, /Duplicate VNDB id/],
    [{ title: "Missing id" }, undefined, /vndb_id required/],
    [{ vndb_id: "v2", slug: "wrong" }, undefined, /slug must equal/],
    [{ vndb_id: "v2" }, { vndb_id: "v3", routes: [{ reviewed: true }] }, /id\/routes mismatch/],
    [{ vndb_id: "v2" }, { vndb_id: "v2", routes: [] }, /id\/routes mismatch/],
  ];
  for (const [metadata, guideData, expected] of cases) {
    const root = await fixture();
    try {
      await game(root, "new-game", metadata, guideData);
      await assert.rejects(loadCatalog(root), expected);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  }
});

test("invalid JSON and non-object catalog are rejected", async () => {
  for (const bad of ["{", "null", "[]"]) {
    const root = await fixture();
    try {
      await mkdir(join(root, "new-game"));
      await writeFile(join(root, "new-game", "catalog.json"), bad);
      await assert.rejects(loadCatalog(root), /Invalid new-game\/catalog.json/);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  }
});

test("discovers existing non-VN game identifiers through per-game catalogs", async () => {
  const root = await fixture();
  try {
    for (const [slug, id] of [
      ["black-matrix-oo", "game:black-matrix-oo"],
      ["arc-the-lad-ii", "game:arc-the-lad-ii"],
    ]) {
      await game(root, slug, { vndb_id: id, title: slug },
        { vndb_id: id, routes: [{ reviewed: true }] });
    }
    const entries = await loadCatalog(root);
    assert.equal(entries["game:black-matrix-oo"].has_guide, true);
    assert.equal(entries["game:arc-the-lad-ii"].slug, "arc-the-lad-ii");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

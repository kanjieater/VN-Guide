import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { test } from "bun:test";

import {
  buildManifest,
  expectedGeneratedFiles,
  findGeneratedDrift,
  landingGames,
  renderLanding,
  syncGeneratedFiles,
} from "../tools/generate.mjs";

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "vnguide-generator-"));
  await mkdir(join(root, "templates"), { recursive: true });
  await writeFile(
    join(root, "games.json"),
    JSON.stringify({
      v1: {
        slug: "日本語-game",
        title: "Roman Title",
        alttitle: "日本語タイトル",
        has_guide: true,
        cover_url: "cover.jpg"
      },
      "game:manual": {
        slug: "manual",
        title: "Manual Game",
        has_guide: false
      }
    })
  );
  await writeFile(join(root, "templates", "landing.html"), "before /* GAMES_DATA */ after");
  await writeFile(join(root, "templates", "guide.html"), "<div id=\"app\"></div>");
  return root;
}

test("generator projects games.json into landing cards and manifests", () => {
  const games = {
    one: { slug: "one", title: "One", alttitle: "一", has_guide: 1, cover_url: "a.jpg" },
    two: { slug: "two", title: "Two" }
  };
  assert.deepEqual(landingGames(games), [
    { slug: "one", title: "One", alttitle: "一", has_guide: true, cover_url: "a.jpg" },
    { slug: "two", title: "Two", alttitle: "", has_guide: false, cover_url: "" }
  ]);
  assert.equal(
    renderLanding("x /* GAMES_DATA */ y", games),
    'x [{"slug": "one", "title": "One", "alttitle": "一", "has_guide": true, "cover_url": "a.jpg"}, {"slug": "two", "title": "Two", "alttitle": "", "has_guide": false, "cover_url": ""}] y'
  );
  assert.equal(buildManifest("One").name, "One ガイド");
});

test("generator check fails on drift, write mode fixes it, and the next check is clean", async () => {
  const root = await fixture();
  try {
    const expected = await expectedGeneratedFiles(root);
    assert.deepEqual([...expected.keys()], [
      "index.html",
      "日本語-game/index.html",
      "日本語-game/manifest.json",
      "manual/index.html",
      "manual/manifest.json"
    ]);

    assert.equal((await findGeneratedDrift(root)).length, 5);
    await assert.rejects(syncGeneratedFiles(root, { check: true }), /Generated files are stale/);

    assert.equal((await syncGeneratedFiles(root)).length, 5);
    assert.equal(await readFile(join(root, "日本語-game", "index.html"), "utf8"), '<div id="app"></div>');
    assert.match(await readFile(join(root, "manual", "manifest.json"), "utf8"), /Manual Game ガイド/);

    assert.deepEqual(await findGeneratedDrift(root), []);
    assert.deepEqual(await syncGeneratedFiles(root, { check: true }), []);

    await writeFile(join(root, "manual", "index.html"), "stale");
    assert.deepEqual(
      (await findGeneratedDrift(root)).map(item => item.relativePath),
      ["manual/index.html"]
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

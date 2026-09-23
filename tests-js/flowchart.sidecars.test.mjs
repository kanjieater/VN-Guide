import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { test } from "bun:test";
import { JSDOM } from "jsdom";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const FLOWCHART_URL = pathToFileURL(join(ROOT, "flowchart.js")).href;
let importCounter = 0;

async function runtime() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>");
  Object.defineProperty(globalThis, "window", {
    configurable: true,
    writable: true,
    value: dom.window,
  });
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    writable: true,
    value: dom.window.document,
  });
  await import(`${FLOWCHART_URL}?sidecar=${++importCounter}`);
  return { dom, api: dom.window.VNFlowchart };
}

async function loadGame(slug) {
  const dir = join(ROOT, slug);
  const guide = JSON.parse(await readFile(join(dir, "guide.json"), "utf8"));
  await Promise.all(guide.routes.map(async route => {
    route.steps = JSON.parse(await readFile(join(dir, `route_${route.id}.json`), "utf8"));
  }));
  return {
    guide,
    sidecar: JSON.parse(await readFile(join(dir, "flowchart.json"), "utf8"))
  };
}

test.serial("every committed detailed sidecar satisfies the runtime contract", async () => {
  const entries = await readdir(ROOT, { withFileTypes: true });
  const slugs = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    try {
      await readFile(join(ROOT, entry.name, "flowchart.json"), "utf8");
      slugs.push(entry.name);
    } catch {}
  }
  assert.ok(slugs.length > 0);

  const { dom, api } = await runtime();
  for (const slug of slugs) {
    const { guide, sidecar } = await loadGame(slug);
    assert.doesNotThrow(() => api.buildEnhancedGraph(guide, sidecar), slug);
  }
  dom.window.close();
});

test.serial("Himawari detailed graph preserves non-flat unlock topology", async () => {
  const { guide, sidecar } = await loadGame("himawari");
  const { dom, api } = await runtime();
  const graph = api.buildEnhancedGraph(guide, sidecar);
  const nodes = new Map(graph.nodes.map(node => [node.id, node]));
  const edges = new Set(graph.edges.map(edge =>
    `${nodes.get(edge.from).label} -> ${nodes.get(edge.to).label} [${edge.kind || "normal"}]`
  ));

  assert.deepEqual(Array.from(nodes.get("sidecar-asuka-late-visits").items), [
    "アリエスとアクアの様子を見てみる",
    "明香と明の所に行く",
    "部長とジョニーが心配だ"
  ]);
  assert.ok(edges.has("STORY -> 2048-2050 [unlock]"));
  assert.ok(edges.has("【アリエス】END -> Tips追加（1周目クリア） [unlock]"));
  assert.ok(edges.has("クリア後 -> Tips [normal]"));
  assert.equal(edges.has("かげろう -> 2048-2050 [normal]"), false);
  dom.window.close();
});

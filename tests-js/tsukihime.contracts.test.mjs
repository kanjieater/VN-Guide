import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "bun:test";
import { createFlowchartRuntime } from "./helpers/flowchart-harness.mjs";

const json = async file => JSON.parse(await readFile(new URL(`../${file}`, import.meta.url), "utf8"));
const [games, guide, research] = await Promise.all([
  json("games.json"), json("tsukihime-remake/guide.json"), json("tsukihime-remake/research.json"),
]);
const routes = await Promise.all(guide.routes.map(async route => ({
  ...route, steps: await json(`tsukihime-remake/route_${route.id}.json`),
})));

test("Tsukihime keeps one explicit Switch target and source record across its catalog and guide", () => {
  const entry = games.v17909;
  assert.equal(entry.slug, "tsukihime-remake");
  assert.ok(!entry.has_guide || guide.routes.every(route => route.reviewed === true),
    "An unapproved Tsukihime draft must remain unavailable in the catalog");
  assert.equal(entry.title, guide.title);
  assert.equal(guide.title, research.title);
  assert.equal(guide.vndb_id, research.vndb_id);
  assert.equal(guide.vndb_id, "v17909");
  assert.deepEqual(entry.guide_target, guide.guide_target);
  assert.deepEqual(guide.guide_target, research.guide_target);
  assert.equal(guide.guide_target.platform, "Nintendo Switch");
  assert.equal(guide.guide_target.url, "https://vndb.org/r82483");
  assert.equal(entry.cover_url, "https://t.vndb.org/cv/86/86686.jpg");
  assert.deepEqual(guide.sources, research.sources);
  assert.deepEqual(routes.map(r => r.id), research.recommended_order);
  assert.deepEqual(research.routes.map(r => r.prerequisites), [[], ["arcueid"], ["ciel_normal"]]);
  for (const route of routes) {
    for (const step of route.steps) {
      for (const field of ["simpleJp", "jpGuide1", "jpGuide2"]) assert.ok(step[field]?.trim(), field);
      assert.equal(typeof step.enGuide, "string");
    }
  }
});

test("Tsukihime's 21 detours return to real checkpoints and the reader recognizes their branches", async () => {
  const runtime = await createFlowchartRuntime();
  const saves = new Set();
  const endings = [];
  try {
    for (const route of routes) {
      let pending = null;
      let checkpoint = null;
      for (const [i, step] of route.steps.entries()) {
        const save = /^セーブ(\d+)$/.exec(step.simpleJp);
        if (save) {
          checkpoint = Number(save[1]);
          assert.equal(checkpoint, saves.size + 1);
          saves.add(checkpoint);
        }
        assert.doesNotMatch(step.simpleJp, /^セーブ\d+をロード$/);
        if (step.badEndPath) {
          assert.equal(pending, null);
          pending = {label: step.badEndPath, checkpoint};
        }
        if (/^BAD END No\.\d{2}$/.test(step.simpleJp)) {
          assert.equal(step.simpleJp, pending?.label);
          endings.push(Number(step.simpleJp.match(/\d+/)[0]));
          assert.equal(route.steps[i + 1]?.isLoad, true);
        }
        const load = /^セーブ(\d+)にロード$/.exec(step.simpleJp);
        if (load) {
          assert.ok(saves.has(Number(load[1])));
          if (step.isLoad) {
            assert.equal(Number(load[1]), pending?.checkpoint);
            assert.equal(route.steps[i - 1].simpleJp, pending.label);
            pending = null;
          } else {
            assert.equal(i, 0);
          }
        }
      }
      assert.equal(pending, null);
      const graph = runtime.api.buildRouteGraph(route);
      assert.equal(graph.nodes.filter(n => n.kind === "branch").length,
        {arcueid: 10, ciel_normal: 8, ciel_extra: 2}[route.id]);
    }
    assert.equal(saves.size, 22);
    assert.deepEqual(endings.toSorted((a, b) => a - b), Array.from({length: 21}, (_, i) => i + 1));
  } finally {
    runtime.dom.window.close();
  }
});

test("Tsukihime preserves delayed No.15 and reconstructs the No.14 conversation only once", () => {
  const steps = routes.find(r => r.id === "ciel_normal").steps;
  const delayed = steps.findIndex(s => s.badEndPath === "BAD END No.15");
  const terminal = steps.findIndex(s => s.simpleJp === "BAD END No.15");
  assert.equal(terminal - delayed, 9);
  assert.equal(steps[terminal + 1].simpleJp, "セーブ14にロード");
  assert.equal(steps[terminal + 2].simpleJp, "そりゃあ痛くなくて効くものを。");
  const early = steps.findIndex(s => s.badEndPath === "BAD END No.14");
  assert.equal(steps[early - 1].simpleJp, "セーブ15");
  assert.equal(steps[early].simpleJp, "問題はない。話は放課後にすればいいし。");
  let detour = false;
  const main = steps.filter(step => {
    if (step.badEndPath) detour = true;
    if (step.isLoad) { detour = false; return false; }
    return !detour;
  });
  assert.equal(main.filter(s => s.simpleJp === "……よくはない。今こそきちんと話すべきだ。").length, 1);
  assert.equal(main.filter(s => s.simpleJp === "……アルクェイドの事なんですが……").length, 1);
});

test("Tsukihime reconciled literals preserve the extracted choice payloads exactly", async () => {
  const evidence = await json("tsukihime-remake/menu-text-evidence.json");
  assert.equal(evidence.target, guide.guide_target.url);
  assert.equal(evidence.choices.length, 13);
  assert.equal(new Set(evidence.choices.map(choice => choice.text_id)).size, 13);
  for (const choice of evidence.choices) {
    const route = routes.find(route => route.id === choice.route);
    assert.equal(route.steps[choice.step].simpleJp, choice.text);
    assert.ok(choice.references.length > 0);
    for (const reference of choice.references) {
      assert.ok(reference.args.split(",").includes(`$${String(choice.text_id).padStart(6, "0")}`));
    }
  }
  for (const id of [42734, 42735]) {
    assert.ok(evidence.choices.find(choice => choice.text_id === id).text.includes("？\u3000と"));
  }
  assert.ok(evidence.choices.find(choice => choice.text_id === 42751).text.includes("眼鏡は"));
});

test("Tsukihime records the owner provenance waiver without dropping source disagreements", async () => {
  const supplement = await readFile(new URL("../tsukihime-remake/prompt_supplement.md", import.meta.url), "utf8");
  const evidence = await json("tsukihime-remake/menu-text-evidence.json");
  assert.ok(supplement.includes("issuecomment-6476454232"));
  assert.ok(research.source_policy.literal_reconciliation.includes("issuecomment-6476454232"));
  for (const choice of evidence.choices) {
    assert.ok(supplement.includes(`| \`route_${choice.route}.json\` | ${choice.step} | ${choice.text_id} |`));
  }
  const silent = routes.find(route => route.id === "ciel_normal").steps[44];
  assert.notEqual(silent.jpGuide1, silent.jpGuide2);
  assert.match(silent.enGuide, /independently reproduced/);
  assert.doesNotMatch(silent.enGuide, /remains unverified/);
});

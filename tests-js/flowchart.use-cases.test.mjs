import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import test from "node:test";

import { JSDOM } from "jsdom";


const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const FLOWCHART_PATH = resolve(ROOT, "flowchart.js");
const FLOWCHART_SOURCE = readFileSync(FLOWCHART_PATH, "utf8");


function loadFlowchart() {
  const dom = new JSDOM("<!doctype html><html><body><div id=\"chart\"></div></body></html>", {
    url: "https://example.test/game/",
    runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  window.requestAnimationFrame = callback => {
    callback(0);
    return 1;
  };

  new vm.Script(FLOWCHART_SOURCE, { filename: FLOWCHART_PATH })
    .runInContext(dom.getInternalVMContext());

  return { dom, window, api: window.VNFlowchart };
}


test("inferred graph models save/load branches and replay-from-start endings", t => {
  const runtime = loadFlowchart();
  t.after(() => runtime.dom.window.close());

  const branched = runtime.api.buildRouteGraph({
    id: "a",
    title: "Route A",
    steps: [
      { simpleJp: "セーブ1" },
      { simpleJp: "危険な選択", badEndPath: "BAD END" },
      { simpleJp: "【BAD】END" },
      { simpleJp: "セーブ1にロード", isLoad: true },
      { simpleJp: "安全な選択" },
      { simpleJp: "【GOOD】END" },
    ],
  });

  const branch = branched.nodes.find(node => node.kind === "branch");
  const danger = branched.nodes.find(node => node.label === "危険な選択");
  const safe = branched.nodes.find(node => node.label === "安全な選択");
  assert.ok(branch);
  assert.equal(danger.kind, "detour");
  assert.ok(branched.edges.some(edge => edge.from === branch.id && edge.to === danger.id));
  assert.ok(branched.edges.some(edge => edge.from === branch.id && edge.to === safe.id));

  const replay = runtime.api.buildRouteGraph({
    id: "replay",
    title: "Replay",
    steps: [
      { simpleJp: "【FIRST】END" },
      { simpleJp: "二周目の選択" },
    ],
  });
  const start = replay.nodes.find(node => node.kind === "route");
  const ending = replay.nodes.find(node => node.kind === "end");
  const secondPass = replay.nodes.find(node => node.label === "二周目の選択");
  assert.ok(replay.edges.some(edge => edge.from === start.id && edge.to === ending.id));
  assert.ok(replay.edges.some(edge => edge.from === start.id && edge.to === secondPass.id));
  assert.equal(
    replay.edges.some(edge => edge.from === ending.id && edge.to === secondPass.id),
    false
  );
});


test("detailed sidecars can group real steps, add annotations, and retain navigation identity", t => {
  const runtime = loadFlowchart();
  t.after(() => runtime.dom.window.close());

  const guide = {
    title: "Detailed VN",
    routes: [
      {
        id: "a",
        title: "Alpha",
        steps: [
          { simpleJp: "A" },
          { simpleJp: "B" },
          { simpleJp: "C" },
        ],
      },
    ],
  };
  const sidecar = {
    version: 1,
    groups: [
      {
        id: "either-order",
        label: "順不同",
        members: [
          { route: "a", step: { simpleJp: "A" } },
          { route: "a", step: { simpleJp: "B" } },
        ],
      },
    ],
    syntheticNodes: [
      {
        id: "note",
        label: "解禁メモ",
        near: { route: "a", step: { simpleJp: "C" } },
        navigable: false,
      },
    ],
    routeLinks: [
      {
        from: { route: "a", step: { simpleJp: "C" } },
        to: { synthetic: "note" },
        kind: "unlock",
      },
    ],
  };

  const graph = runtime.api.buildEnhancedGraph(guide, sidecar);
  const group = graph.nodes.find(node => node.id === "sidecar-either-order");
  const note = graph.nodes.find(node => node.id === "sidecar-note");

  assert.deepEqual(Array.from(group.items), ["A", "B"]);
  assert.equal(group.routeId, "a");
  assert.equal(group.stepIndex, 0);
  assert.deepEqual(Array.from(group.currentStepIndexes), [0, 1]);
  assert.equal(note.stepIndex, null);
  assert.ok(
    graph.edges.some(edge =>
      edge.to === note.id && edge.kind === "unlock"
    )
  );

  assert.deepEqual(
    runtime.api.nodeProgressState(group, {
      seen: { a: 1 },
      current: { a: 1 },
    }),
    { seen: true, current: true, known: true }
  );
  assert.deepEqual(
    runtime.api.nodeProgressState(note, {
      seen: { a: 2 },
      current: { a: 2 },
    }),
    { seen: false, current: false, known: false }
  );
});


test("sidecar validation fails closed on ambiguous or unsupported topology", t => {
  const runtime = loadFlowchart();
  t.after(() => runtime.dom.window.close());

  const guide = {
    routes: [
      {
        id: "a",
        title: "Alpha",
        steps: [{ simpleJp: "A" }, { simpleJp: "B" }],
      },
    ],
  };

  assert.throws(
    () => runtime.api.validateSidecar(guide, { version: 2 }),
    /version/
  );
  assert.throws(
    () => runtime.api.validateSidecar(guide, { version: 1, mystery: true }),
    /unsupported field/
  );
  assert.throws(
    () => runtime.api.validateSidecar(guide, {
      version: 1,
      addEdges: [
        {
          from: { route: "a", step: { simpleJp: "A", occurrence: 0 } },
          to: { route: "a", step: { simpleJp: "B" } },
        },
      ],
    }),
    /positive integer/
  );
});


test("rendered flowchart supports pointer, keyboard, wheel, pinch, and zoom-control navigation", t => {
  const runtime = loadFlowchart();
  t.after(() => runtime.dom.window.close());

  const container = runtime.window.document.getElementById("chart");
  const navigations = [];

  runtime.api.render(
    container,
    {
      title: "Interactive VN",
      routes: [
        {
          id: "a",
          title: "Alpha",
          steps: [
            { simpleJp: "セーブ1" },
            { simpleJp: "Choice A" },
            { simpleJp: "セーブ1にロード", isLoad: true },
            { simpleJp: "Choice B" },
            { simpleJp: "【GOOD】END" },
          ],
        },
      ],
    },
    (routeId, stepIndex) => navigations.push([routeId, stepIndex]),
    null,
    { seen: { a: 3 }, current: { a: 3 } }
  );

  assert.match(container.querySelector(".flowchart-note").textContent, /推定分岐図/);
  assert.ok(container.querySelector(".flow-node-current"));
  assert.ok(container.querySelector(".flow-node-seen"));
  assert.ok(container.querySelector(".flow-node-unseen"));

  const controls = Array.from(container.querySelectorAll(".flowchart-zoom button"));
  assert.deepEqual(controls.map(button => button.textContent), ["−", "全体", "＋"]);

  const link = Array.from(container.querySelectorAll("g[role=\"link\"]"))
    .find(node => node.getAttribute("aria-label").includes("Choice B"));
  assert.ok(link);

  link.dispatchEvent(new runtime.window.MouseEvent("click", { bubbles: true }));
  link.dispatchEvent(new runtime.window.KeyboardEvent("keydown", {
    key: "Enter",
    bubbles: true,
    cancelable: true,
  }));
  assert.deepEqual(navigations, [["a", 3], ["a", 3]]);

  const scroller = container.querySelector(".flowchart-canvas");
  const svg = scroller.querySelector("svg");
  const initialWidth = svg.style.width;

  controls[2].click();
  assert.notEqual(svg.style.width, initialWidth);

  scroller.dispatchEvent(new runtime.window.WheelEvent("wheel", {
    deltaY: -100,
    clientX: 50,
    bubbles: true,
    cancelable: true,
  }));

  const touchStart = new runtime.window.Event("touchstart", {
    bubbles: true,
    cancelable: true,
  });
  Object.defineProperty(touchStart, "touches", {
    value: [
      { clientX: 10, clientY: 10 },
      { clientX: 110, clientY: 10 },
    ],
  });
  scroller.dispatchEvent(touchStart);

  const touchMove = new runtime.window.Event("touchmove", {
    bubbles: true,
    cancelable: true,
  });
  Object.defineProperty(touchMove, "touches", {
    value: [
      { clientX: 0, clientY: 10 },
      { clientX: 140, clientY: 10 },
    ],
  });
  scroller.dispatchEvent(touchMove);

  const touchEnd = new runtime.window.Event("touchend", { bubbles: true });
  Object.defineProperty(touchEnd, "touches", { value: [] });
  scroller.dispatchEvent(touchEnd);

  controls[1].click();
  assert.match(container.querySelector(".flowchart-zoom-readout").textContent, /%/);
});


test("invalid detailed sidecar visibly falls back to the inferred graph", t => {
  const runtime = loadFlowchart();
  t.after(() => runtime.dom.window.close());

  const warnings = [];
  runtime.window.console.warn = (...args) => warnings.push(args);

  const container = runtime.window.document.getElementById("chart");
  runtime.api.render(
    container,
    {
      title: "Fallback VN",
      routes: [
        {
          id: "a",
          title: "Alpha",
          steps: [{ simpleJp: "A" }],
        },
      ],
    },
    () => {},
    { version: 99 },
    {}
  );

  assert.equal(warnings.length, 1);
  assert.match(container.querySelector(".flowchart-note").textContent, /推定分岐図/);
  assert.equal(container.querySelectorAll(".flowchart-route").length, 1);
});

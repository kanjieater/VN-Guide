import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState, stateKey } from "./helpers/guide-app-harness.mjs";

const nav = state => ({ vng: true, ...state });

test("reload restores a flowchart preview without committing saved progress", async () => {
  const guide = {
    title: "Preview Reload VN",
    routes: [{
      id: "a",
      title: "Alpha",
      steps: [
        { simpleJp: "A1" },
        { simpleJp: "A2" },
        { simpleJp: "A3" },
        { simpleJp: "A4" },
      ],
    }],
  };
  const saved = {
    currentRoute: "a",
    progress: { a: 1 },
    seenProgress: { a: 1 },
  };

  const app = await bootApp({
    guide,
    storage: { [stateKey("/game/")]: JSON.stringify(saved) },
    initialHistory: [
      { state: nav({ view: "route", routeId: "a", step: 1, fromView: "home" }), url: "/game/#view=route&route=a&step=1&from=home" },
      { state: nav({ view: "flowchart" }), url: "/game/#view=flowchart" },
      { state: nav({ view: "route", routeId: "a", step: 2, preview: true, fromView: "flowchart" }), url: "/game/#view=route&route=a&step=2&from=flowchart&preview=1" },
    ],
  });

  assert.equal(app.window.history.state.preview, true);
  assert.match(app.window.document.getElementById("step-counter").textContent, /3 \/ 4 .*プレビュー/);
  assert.equal(readState(app.window).progress.a, 1);
  assert.equal(readState(app.window).seenProgress.a, 1);

  app.dom.window.close();
});

import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState, settle, stateKey } from "./helpers/guide-app-harness.mjs";

test("reader restores progress, finishes a route, backtracks, and enters the next route", async () => {
  const guide = {
    title: "Demo VN",
    routes: [
      { id: "a", title: "Alpha", portrait: "alpha.jpg", stepCount: 2, reviewed: true },
      { id: "b", title: "Beta", portrait: "beta.jpg", stepCount: 1, reviewed: false },
    ],
  };
  const routes = {
    a: [{ simpleJp: "A1" }, { simpleJp: "A2" }],
    b: [{ simpleJp: "B1" }],
  };
  const saved = {
    currentRoute: "a",
    progress: { a: 1 },
    seenProgress: { a: 1 },
  };
  const app = await bootApp({
    guide,
    routes,
    storage: { [stateKey("/game/")]: JSON.stringify(saved) },
  });

  await app.window.startRoute("a");
  assert.equal(app.window.document.getElementById("step-counter").textContent, "2 / 2 (100%)");

  await app.window.nextStep();
  assert.equal(app.window.document.getElementById("step-counter").textContent, "ルート完了");
  assert.match(app.window.document.getElementById("simple-instruction").textContent, /Beta/);

  await app.window.prevStep();
  await settle();
  assert.equal(app.window.document.getElementById("step-counter").textContent, "2 / 2 (100%)");
  assert.equal(readState(app.window).progress.a, 1);

  await app.window.nextStep();
  await app.window.nextStep();
  assert.equal(readState(app.window).currentRoute, "b");
  assert.equal(readState(app.window).progress.b, 0);
  assert.equal(app.window.document.getElementById("step-counter").textContent, "1 / 1 (100%)");

  app.window.goHome();
  assert.equal(readState(app.window).currentRoute, null);
  assert.match(app.window.document.getElementById("route-list").textContent, /Alpha/);

  app.dom.window.close();
});

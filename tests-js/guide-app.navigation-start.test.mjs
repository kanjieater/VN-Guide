import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState, stateKey } from "./helpers/guide-app-harness.mjs";

test("reader starts, advances, and persists progress", async () => {
  const guide = {
    title: "Demo VN",
    generated_at: "2026-09-23T12:00:00Z",
    guide_target: {
      label: "Demo Edition",
      platform: "Nintendo Switch",
      url: "https://example.test/release",
    },
    routes: [
      { id: "a", title: "Alpha", portrait: "alpha.jpg", stepCount: 2, reviewed: true },
      { id: "b", title: "Beta", portrait: "beta.jpg", stepCount: 1, reviewed: false },
    ],
  };
  const routes = {
    a: [{ simpleJp: "A1" }, { simpleJp: "A2" }],
    b: [{ simpleJp: "B1" }],
  };
  const app = await bootApp({ guide, routes });

  assert.equal(app.window.document.title, "Demo VN ガイド");
  assert.match(app.window.document.getElementById("route-list").textContent, /ルート 1/);
  assert.doesNotMatch(app.window.document.getElementById("route-list").textContent, /Alpha/);
  assert.match(app.window.document.getElementById("guide-target").textContent, /Demo Edition/);

  await app.window.startRoute("a");
  assert.equal(app.window.document.getElementById("step-counter").textContent, "1 / 2 (50%)");

  await app.window.nextStep();
  assert.equal(readState(app.window).progress.a, 1);
  assert.ok(app.window.localStorage.getItem(stateKey("/game/")));

  app.dom.window.close();
});

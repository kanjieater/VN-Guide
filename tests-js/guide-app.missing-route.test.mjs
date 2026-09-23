import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState } from "./helpers/guide-app-harness.mjs";

test("missing route fetch recovers home without corrupting progress", async () => {
  const app = await bootApp({
    guide: {
      title: "Incomplete",
      routes: [{ id: "missing", title: "Missing", stepCount: 2 }],
    },
  });

  await app.window.startRoute("missing");
  assert.ok(app.window.document.getElementById("view-home").classList.contains("active"));
  assert.match(app.window.document.getElementById("home-status").textContent, /生成中/);
  assert.deepEqual(readState(app.window), {
    currentRoute: null,
    progress: {},
    seenProgress: {},
  });

  app.dom.window.close();
});

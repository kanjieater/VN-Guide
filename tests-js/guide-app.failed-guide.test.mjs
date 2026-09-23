import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp } from "./helpers/guide-app-harness.mjs";

test("failed guide fetch leaves a recoverable home view", async () => {
  const app = await bootApp({
    guide: { routes: [] },
    guideFetchOk: false,
  });

  assert.ok(app.window.document.getElementById("view-home").classList.contains("active"));
  assert.match(app.window.document.getElementById("home-status").textContent, /ガイド作成中/);

  app.dom.window.close();
});

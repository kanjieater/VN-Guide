import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp } from "./helpers/guide-app-harness.mjs";

test("linear games show real section titles and suppress the VN flowchart", async () => {
  const app = await bootApp({
    guide: {
      title: "Linear Game",
      vndb_id: "game:arc-the-lad-2",
      routes: [{ id: "chapter-1", title: "Chapter 1", stepCount: 1 }],
    },
    routes: { "chapter-1": [{ simpleJp: "Proceed" }] },
  });

  assert.match(app.window.document.getElementById("route-list").textContent, /セクション 1/);
  assert.doesNotMatch(app.window.document.getElementById("route-list").textContent, /Chapter 1/);
  assert.equal(app.window.document.getElementById("btn-flowchart").style.display, "none");

  app.window.showSettings();
  app.window.toggleSetting("blurPortraits");
  app.window.goHome();
  assert.match(app.window.document.getElementById("route-list").textContent, /Chapter 1/);
  await app.window.showFlowchart();
  assert.ok(app.window.document.getElementById("view-home").classList.contains("active"));

  app.dom.window.close();
});

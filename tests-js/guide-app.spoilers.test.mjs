import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp } from "./helpers/guide-app-harness.mjs";

test("spoiler protection can be disabled and the setting persists", async () => {
  const app = await bootApp({
    guide: {
      title: "Spoiler VN",
      routes: [{ id: "a", title: "Secret Heroine", portrait: "secret.jpg", stepCount: 2 }],
    },
    routes: { a: [{ simpleJp: "First" }, { simpleJp: "Second" }] },
  });

  let routeList = app.window.document.getElementById("route-list");
  assert.match(routeList.textContent, /ルート 1/);
  assert.ok(routeList.querySelector("img").classList.contains("locked"));

  app.window.showSettings();
  app.window.toggleSetting("blurPortraits");
  assert.deepEqual(JSON.parse(app.window.localStorage.getItem("vng_settings")), {
    blurPortraits: false,
  });

  app.window.goHome();
  routeList = app.window.document.getElementById("route-list");
  assert.match(routeList.textContent, /Secret Heroine/);
  assert.equal(routeList.querySelector("img").classList.contains("locked"), false);

  app.dom.window.close();
});

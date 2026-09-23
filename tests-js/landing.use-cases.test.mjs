import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "bun:test";
import { JSDOM } from "jsdom";

import { renderLanding } from "../tools/generate.mjs";

test("landing search and playing filter use real saved guide progress", async () => {
  const template = await readFile(new URL("../templates/landing.html", import.meta.url), "utf8");
  const html = renderLanding(template, {
    one: { slug: "日本語-game", title: "Roman One", alttitle: "日本語一", has_guide: true },
    two: { slug: "two", title: "Roman Two", has_guide: true }
  });

  const dom = new JSDOM(html, {
    url: "https://example.test/",
    runScripts: "dangerously",
    beforeParse(window) {
      window.fetch = async url => ({
        ok: true,
        async json() {
          return String(url).includes("日本語-game")
            ? { routes: [{ id: "route", stepCount: 4 }] }
            : { routes: [{ id: "route", stepCount: 2 }] };
        }
      });
    }
  });
  const { window } = dom;

  const encodedPath = new URL("./%E6%97%A5%E6%9C%AC%E8%AA%9E-game/", window.location.href).pathname;
  window.localStorage.setItem(
    "guide_" + encodedPath.replace(/\//g, "_"),
    JSON.stringify({ progress: { route: 1 } })
  );

  await window.render();
  assert.match(window.document.getElementById("game-list").textContent, /日本語一/);

  window.document.getElementById("search").value = "two";
  await window.render();
  assert.match(window.document.getElementById("game-list").textContent, /Roman Two/);
  assert.doesNotMatch(window.document.getElementById("game-list").textContent, /日本語一/);

  window.document.getElementById("search").value = "";
  window.setFilter("playing");
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(window.document.getElementById("game-list").textContent, /日本語一/);
  assert.doesNotMatch(window.document.getElementById("game-list").textContent, /Roman Two/);

  dom.window.close();
});

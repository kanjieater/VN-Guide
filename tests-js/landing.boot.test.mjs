import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "bun:test";
import { JSDOM } from "jsdom";

const BOOT_URL = new URL("../landing-boot.js", import.meta.url).href;

test("saved landing tabs are selected before the homepage app starts", async () => {
  const template = await readFile(new URL("../templates/landing.html", import.meta.url), "utf8");
  const dom = new JSDOM(template, {
    url: "https://example.test/",
    runScripts: "outside-only",
  });
  const { window } = dom;

  window.localStorage.setItem("vn-guide-sort", "alpha");
  window.localStorage.setItem("vn-guide-filter", "playing");

  Object.defineProperty(globalThis, "window", {
    configurable: true,
    writable: true,
    value: window,
  });
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    writable: true,
    value: window.document,
  });
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    writable: true,
    value: window.localStorage,
  });

  await import(BOOT_URL);

  assert.equal(window.document.documentElement.dataset.vngSort, "alpha");
  assert.equal(window.document.documentElement.dataset.vngFilter, "playing");
  assert.equal(window.document.querySelector("#btn-all").classList.contains("active"), false);
  assert.equal(window.document.querySelector("#btn-recent").classList.contains("active"), false);
  assert.equal(
    window.document.querySelector('html[data-vng-filter="playing"] #btn-playing')?.id,
    "btn-playing"
  );
  assert.equal(
    window.document.querySelector('html[data-vng-sort="alpha"] #btn-alpha')?.id,
    "btn-alpha"
  );

  const selectors = [...window.document.styleSheets]
    .flatMap(sheet => [...sheet.cssRules])
    .map(rule => rule.selectorText || "");
  assert.ok(selectors.some(selector => selector.includes('html[data-vng-filter="playing"] #btn-playing')));
  assert.ok(selectors.some(selector => selector.includes('html[data-vng-filter="all"] #btn-all')));

  const headHtml = window.document.head.innerHTML;
  assert.ok(
    headHtml.indexOf('landing-boot.js') < headHtml.indexOf("<style>"),
    "saved tab state must be applied by a blocking head script before controls can paint"
  );

  dom.window.close();
});

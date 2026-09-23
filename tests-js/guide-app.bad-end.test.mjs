import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState } from "./helpers/guide-app-harness.mjs";

test("bad-end instructions remain understandable in slide and jump-list views", async () => {
  const app = await bootApp({
    guide: {
      title: "Bad End VN",
      routes: [{
        id: "a",
        title: "Alpha",
        steps: [
          {
            simpleJp: "危険な選択",
            badEndPath: "BAD END 1",
            badEnd: { choice: "<危険>", end: "GAME OVER" },
            jpGuide1: "攻略①",
          },
          { simpleJp: "セーブ1にロード", isLoad: true },
          { simpleJp: "安全な選択", enGuide: "Safe choice" },
        ],
      }],
    },
  });

  await app.window.startRoute("a");
  const badEnd = app.window.document.getElementById("detail-bad-end");
  assert.match(badEnd.textContent, /<危険>.*GAME OVER/);
  assert.match(badEnd.innerHTML, /&lt;危険&gt;/);

  app.window.toggleDetails();
  assert.equal(app.window.document.getElementById("details-section").style.display, "block");
  app.window.toggleDetails();
  assert.equal(app.window.document.getElementById("details-section").style.display, "none");

  await app.window.nextStep();
  assert.match(app.window.document.getElementById("simple-instruction").textContent, /BAD END 1 ⚠ セーブ1にロード/);

  app.window.showJump();
  assert.match(app.window.document.getElementById("jump-list").textContent, /BAD END 1 ⚠ セーブ1にロード/);

  app.window.jumpTo(2);
  assert.equal(readState(app.window).progress.a, 2);
  assert.equal(app.window.document.getElementById("simple-instruction").textContent, "安全な選択");

  app.dom.window.close();
});

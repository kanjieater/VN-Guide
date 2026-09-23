import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, readState } from "./helpers/guide-app-harness.mjs";

test("flowchart exploration is preview-only until the reader explicitly continues", async () => {
  const guide = {
    title: "Preview VN",
    routes: [{
      id: "a",
      title: "Alpha",
      reviewed: true,
      steps: [
        { simpleJp: "A1" },
        { simpleJp: "A2" },
        { simpleJp: "A3" },
        { simpleJp: "A4" },
      ],
    }],
  };
  const app = await bootApp({ guide });

  await app.window.startRoute("a");
  await app.window.nextStep();
  assert.equal(readState(app.window).progress.a, 1);

  let renderArgs = null;
  app.window.VNFlowchart = {
    deriveCurrentProgress(_routes, progress) {
      return { ...progress };
    },
    render(...args) {
      renderArgs = args;
      args[0].textContent = "rendered";
    },
  };

  await app.window.showFlowchart();
  assert.equal(app.window.document.getElementById("flowchart-content").textContent, "rendered");
  assert.equal(renderArgs[4].current.a, 1);
  assert.equal(renderArgs[4].seen.a, 1);

  await app.window.jumpFromFlowchart("a", 2);
  assert.equal(readState(app.window).progress.a, 1);
  assert.match(app.window.document.getElementById("step-counter").textContent, /3 \/ 4 .*プレビュー/);
  assert.equal(app.window.document.getElementById("btn-next").textContent, "ここから進む ▶");

  await app.window.prevStep();
  assert.equal(readState(app.window).progress.a, 1);
  assert.match(app.window.document.getElementById("step-counter").textContent, /2 \/ 4 .*プレビュー/);

  await app.window.jumpFromFlowchart("a", 2);
  await app.window.nextStep();
  assert.equal(readState(app.window).progress.a, 3);
  assert.equal(readState(app.window).seenProgress.a, 3);
  assert.equal(app.window.document.getElementById("step-counter").textContent, "4 / 4 (100%)");

  app.dom.window.close();
});

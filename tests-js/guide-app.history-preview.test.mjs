import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, moveHistory, readState } from "./helpers/guide-app-harness.mjs";

test("flowchart preview survives Back/Forward without committing progress", async () => {
  const guide = {
    title: "Preview History VN",
    routes: [{
      id: "a",
      title: "Alpha",
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

  app.window.VNFlowchart = {
    deriveCurrentProgress(_routes, progress) {
      return { ...progress };
    },
    render(target) {
      target.textContent = "chart";
    },
  };

  await app.window.showFlowchart();
  await app.window.jumpFromFlowchart("a", 2);
  assert.equal(app.window.history.state.preview, true);
  assert.equal(readState(app.window).progress.a, 1);

  await moveHistory(app.window, "back");
  assert.equal(app.window.history.state.view, "flowchart");
  assert.equal(readState(app.window).progress.a, 1);
  assert.equal(app.window.document.getElementById("flowchart-content").textContent, "chart");

  await moveHistory(app.window, "forward");
  assert.equal(app.window.history.state.view, "route");
  assert.equal(app.window.history.state.preview, true);
  assert.match(app.window.document.getElementById("step-counter").textContent, /3 \/ 4 .*プレビュー/);
  assert.equal(readState(app.window).progress.a, 1);

  app.dom.window.close();
});

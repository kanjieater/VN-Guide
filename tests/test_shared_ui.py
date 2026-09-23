import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "guide-app.js"
STYLE = ROOT / "style.css"


class SharedGuideUiTests(unittest.TestCase):
    def test_shared_javascript_owns_all_guide_views_and_metadata_order(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("function mountAppShell()", source)
        for view_id in ("view-home", "view-slide", "view-jump", "view-flowchart", "view-settings"):
            self.assertIn(f'id="{view_id}"', source)
        updated = source.index('id="guide-updated"')
        target = source.index('id="guide-target"')
        self.assertLess(updated, target)
        self.assertIn('class="guide-meta"', source)

    def test_flowchart_is_generic_and_vn_only(self):
        source = APP.read_text(encoding="utf-8")
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        self.assertIn('id="btn-flowchart"', source)
        self.assertIn('aria-label="分岐図"', source)
        self.assertIn('if (isLinearGameGuide()) return;', source)
        self.assertIn('async function jumpFromFlowchart(routeId, stepIndex)', source)
        loader = source[source.index("async function loadFlowchartRenderer()"):source.index("async function showFlowchart()")]
        self.assertIn('const v = window.__guideAssetVersion || Date.now();', loader)
        self.assertIn('script.src = "../flowchart.js?v=" + v;', loader)
        self.assertNotIn("guideData.generated_at", loader)
        self.assertIn('role: "link"', flowchart)
        self.assertIn('tabindex: "0"', flowchart)
        self.assertIn('fit.textContent = "全体"', flowchart)
        self.assertIn('zoomOut.textContent = "−"', flowchart)
        self.assertIn('zoomIn.textContent = "＋"', flowchart)
        self.assertIn("requestAnimationFrame(() => {", flowchart)
        self.assertIn("zoomGroup.refresh(zoomController)", flowchart)
        self.assertIn("async function loadFlowchartSidecar()", source)
        self.assertIn(
            'window.VNFlowchart.render(content, guideData, jumpFromFlowchart, sidecar, {',
            source,
        )
        self.assertIn("function validateSidecar(guideData, sidecar)", flowchart)
        self.assertIn("function buildEnhancedGraph(guideData, sidecar)", flowchart)
        self.assertIn("validateSidecar(guideData, sidecar);", flowchart)
        self.assertNotIn("検証済みの補足トポロジー", flowchart)
        self.assertIn("Flowchart sidecar rejected; falling back to inferred graph.", flowchart)
        self.assertIn('buildRouteGraph', flowchart)
        self.assertIn('fetch("./flowchart.json?v=" + Date.now())', source)
        self.assertNotIn('fetch("./flowchart.json', flowchart)

    def test_flowchart_uses_one_shared_zoom_controller_for_all_route_sections(self):
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        self.assertIn("function createZoomGroup(container)", flowchart)
        self.assertIn("const zoomGroup = createZoomGroup(container);", flowchart)
        self.assertIn("renderRoute(route, onNavigate, progressState, zoomGroup)", flowchart)
        self.assertIn("zoomGroup.zoomBy(factor, zoomController, event.clientX)", flowchart)

    def test_flowchart_vertical_scroll_is_not_trapped_by_horizontal_canvas(self):
        style = STYLE.read_text(encoding="utf-8")
        self.assertIn("min-height: 0;", style)
        self.assertIn("overscroll-behavior-x: contain;", style)
        self.assertIn("overscroll-behavior-y: auto;", style)

    def test_flowchart_supports_wheel_and_pinch_zoom_anywhere_on_canvas(self):
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")
        self.assertIn('scroller.addEventListener("wheel"', flowchart)
        self.assertIn('scroller.addEventListener("touchstart"', flowchart)
        self.assertIn('scroller.addEventListener("touchmove"', flowchart)
        self.assertIn("function zoomAtScale(nextScale, clientX)", flowchart)
        self.assertIn("event.preventDefault();", flowchart)
        self.assertIn("touch-action: pan-x pan-y;", style)

    def test_flowchart_zoom_controls_float_bottom_right_with_touch_targets(self):
        style = STYLE.read_text(encoding="utf-8")
        self.assertIn("position: fixed;", style)
        self.assertIn("bottom: calc(env(safe-area-inset-bottom, 0px) + 14px);", style)
        self.assertIn("right: max(12px, calc((100vw - 600px) / 2 + 12px));", style)
        self.assertIn("width: 48px;", style)
        self.assertIn("height: 48px;", style)

    def test_flowchart_nodes_receive_seen_current_and_unseen_states(self):
        source = APP.read_text(encoding="utf-8")
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")
        self.assertIn("seenProgress", source)
        self.assertIn("function nodeProgressState(node, progressState)", flowchart)
        self.assertIn("flow-node-seen", flowchart)
        self.assertIn("flow-node-current", flowchart)
        self.assertIn("flow-node-unseen", flowchart)
        self.assertIn(".flow-node-seen .flow-node-shape", style)
        self.assertIn(".flow-node-current .flow-node-shape", style)
        self.assertIn(".flow-node-unseen .flow-node-shape", style)

    def test_synthetic_progress_uses_neutral_visual_state(self):
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")
        self.assertIn('return { seen: false, current: false, known: false };', flowchart)
        self.assertIn('" flow-node-neutral"', flowchart)
        self.assertIn(".flow-node-neutral .flow-node-shape", style)

    def test_existing_route_spoiler_masking_applies_to_games_and_flowcharts(self):
        source = APP.read_text(encoding="utf-8")
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        self.assertIn(
            'const hiddenTitle = isLinearGame ? `セクション ${routeIdx + 1}` : `ルート ${routeIdx + 1}`;',
            source,
        )
        self.assertIn(
            "const displayTitle = (settings.blurPortraits && !hasProgress) ? hiddenTitle : r.title;",
            source,
        )
        self.assertIn("hideRouteTitles: settings.blurPortraits", source)
        self.assertIn("routeProgress: state.progress", source)
        self.assertIn("function routeTitleHidden(routeId, progressState)", flowchart)
        self.assertIn('node.kind === "route" && routeTitleHidden(node.routeId, progressState)', flowchart)
        self.assertNotIn('"？？？"', flowchart)
        self.assertNotIn("hideSpoilers", source)

    def test_flowchart_current_marker_uses_single_derived_stage(self):
        source = APP.read_text(encoding="utf-8")
        flowchart = (ROOT / "flowchart.js").read_text(encoding="utf-8")
        self.assertIn("function deriveCurrentProgress(routes, progressMap)", flowchart)
        self.assertIn(
            "current: window.VNFlowchart.deriveCurrentProgress(",
            source,
        )
        self.assertNotIn("current: state.progress,", source)

    def test_flowchart_click_is_preview_only_until_next(self):
        source = APP.read_text(encoding="utf-8")
        start = source.index("async function jumpFromFlowchart")
        end = source.index("// ── Slide", start)
        jump = source[start:end]
        self.assertIn("flowchartPreview =", jump)
        self.assertNotIn("state.progress[route.id] = target", jump)
        self.assertNotIn("saveState();", jump)

        next_start = source.index("async function nextStep()")
        next_end = source.index("async function prevStep()", next_start)
        next_step = source[next_start:next_end]
        self.assertIn("if (flowchartPreview && flowchartPreview.routeId === route.id)", next_step)
        self.assertIn("state.progress[route.id] = previewIndex + 1;", next_step)
        self.assertIn("saveState();", next_step)

    def test_flowchart_preview_is_visibly_labeled_and_non_destructive_backwards(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('" · プレビュー"', source)
        self.assertIn('"ここから進む ▶"', source)
        prev_start = source.index("async function prevStep()")
        prev_end = source.index("function toggleDetails()", prev_start)
        prev = source[prev_start:prev_end]
        self.assertIn("flowchartPreview.stepIndex -= 1;", prev)
        preview_branch = prev[prev.index("if (flowchartPreview"):prev.index("const idx =", prev.index("if (flowchartPreview"))]
        self.assertNotIn("saveState();", preview_branch)

    def test_first_step_can_backtrack_to_previous_route_transition(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            'document.getElementById("btn-prev").disabled = idx === 0 && !priorRoute;',
            source,
        )
        self.assertIn(
            'renderRouteTransition(route, priorRoute, "backward");',
            source,
        )

    def test_transition_back_restores_saved_previous_route_position(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            'await startRoute(fromRoute.id, { fromView: "transition" });',
            source,
        )
        self.assertNotIn("state.progress[loaded.id] = loaded.steps.length - 1;", source)


    def test_browser_history_tracks_all_shared_screens(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('window.addEventListener("popstate"', source)
        self.assertIn('writeNavigation({ view: "home" }, "replace");', source)
        self.assertIn('writeNavigation({ view: "flowchart" });', source)
        self.assertIn('writeNavigation({ view: "settings" });', source)
        self.assertIn('writeNavigation({ view: "jump", routeId: route.id });', source)
        self.assertIn('view: "transition"', source)

    def test_route_steps_replace_history_instead_of_flooding_it(self):
        source = APP.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            source.count('fromView: currentNavigation().fromView || null'),
            2,
        )
        self.assertGreaterEqual(source.count('}, "replace");'), 5)

    def test_auxiliary_back_controls_use_browser_history(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('onclick="closeFlowchart()"', source)
        self.assertIn('onclick="closeSettings()"', source)
        self.assertIn("function closeFlowchart() {\n  history.back();\n}", source)
        self.assertIn("function closeSettings() {\n  history.back();\n}", source)
        self.assertIn("function resumeSlide() {\n  history.back();\n}", source)

    def test_flowchart_preview_gets_history_entry_without_committing_progress(self):
        source = APP.read_text(encoding="utf-8")
        start = source.index("async function jumpFromFlowchart")
        end = source.index("// ── Slide", start)
        jump = source[start:end]
        self.assertIn('fromView: "flowchart"', jump)
        self.assertIn("preview: true", jump)
        self.assertIn("flowchartPreview =", jump)
        self.assertNotIn("state.progress[route.id] = target", jump)
        self.assertNotIn("saveState();", jump)

    def test_reload_preserves_existing_app_owned_history_entry(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            "const existingNavigation = history.state && history.state[NAV_STATE_KEY]",
            source,
        )
        self.assertIn(
            "const requestedNavigation = existingNavigation || navigationFromLocation();",
            source,
        )
        self.assertIn(
            "if (existingNavigation) {\n    await applyNavigation(existingNavigation);\n  } else {",
            source,
        )

    def test_preview_state_round_trips_through_hash_navigation(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('if (nav.preview) params.set("preview", "1");', source)
        self.assertIn('preview: params.get("preview") === "1"', source)
        self.assertIn("if (nav.preview) {", source)
        self.assertIn("flowchartPreview = { routeId: route.id, stepIndex: targetStep };", source)

    def test_async_navigation_ignores_stale_route_work(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("let navigationApplyEpoch = 0;", source)
        self.assertGreaterEqual(
            source.count("const applyEpoch = ++navigationApplyEpoch;"),
            3,
        )
        self.assertGreaterEqual(
            source.count("applyEpoch !== navigationApplyEpoch"),
            4,
        )

    def test_slow_start_route_cannot_resurrect_after_browser_back(self):
        source = APP.read_text(encoding="utf-8")
        start_route = source.split("async function startRoute", 1)[1].split(
            "// ── Flowchart", 1
        )[0]
        self.assertIn("const applyEpoch = ++navigationApplyEpoch;", start_route)
        self.assertIn("const sourceUrl = location.href;", start_route)
        self.assertIn("const route = await ensureRouteLoaded(id);", start_route)
        self.assertIn(
            "applyEpoch !== navigationApplyEpoch || location.href !== sourceUrl",
            start_route,
        )
        self.assertLess(
            start_route.index("applyEpoch !== navigationApplyEpoch"),
            start_route.index("state.currentRoute = id;"),
        )

    def test_navigation_writes_cancel_outstanding_async_route_work(self):
        source = APP.read_text(encoding="utf-8")
        write_navigation = source.split("function writeNavigation", 1)[1].split(
            "function currentNavigation", 1
        )[0]
        self.assertIn("navigationApplyEpoch += 1;", write_navigation)

    def test_flowchart_jump_cannot_complete_after_newer_navigation(self):
        source = APP.read_text(encoding="utf-8")
        flowchart_jump = source.split("async function jumpFromFlowchart", 1)[1].split(
            "// ── Slide", 1
        )[0]
        self.assertIn("const applyEpoch = ++navigationApplyEpoch;", flowchart_jump)
        self.assertIn("const sourceUrl = location.href;", flowchart_jump)
        self.assertIn("location.href !== sourceUrl", flowchart_jump)

    def test_route_cards_share_uniform_minimum_height(self):
        source = STYLE.read_text(encoding="utf-8")
        self.assertIn("min-height: 90px;", source)
        self.assertNotIn("\n  height: 90px;\n  min-height: 90px;", source)


if __name__ == "__main__":
    unittest.main()

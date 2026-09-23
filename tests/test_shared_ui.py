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
        self.assertIn('window.VNFlowchart.render(content, guideData);', source)
        self.assertIn('buildRouteGraph', flowchart)
        self.assertNotIn("flowchart.json", source)
        self.assertNotIn("flowchart.json", flowchart)

    def test_first_step_can_backtrack_to_previous_route_transition(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            'document.getElementById("btn-prev").disabled = idx === 0 && !priorRoute;',
            source,
        )
        self.assertIn(
            "if (priorRoute) {\n    renderRouteTransition(route, priorRoute);",
            source,
        )

    def test_transition_back_restores_saved_previous_route_position(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("await startRoute(fromRoute.id);", source)
        self.assertNotIn("state.progress[loaded.id] = loaded.steps.length - 1;", source)

    def test_route_cards_share_uniform_minimum_height(self):
        source = STYLE.read_text(encoding="utf-8")
        self.assertIn("min-height: 90px;", source)
        self.assertNotIn("\n  height: 90px;\n  min-height: 90px;", source)


if __name__ == "__main__":
    unittest.main()

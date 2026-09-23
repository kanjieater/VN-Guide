import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "guide-app.js"
STYLE = ROOT / "style.css"


class SharedGuideUiTests(unittest.TestCase):
    def test_shared_javascript_owns_all_guide_views_and_metadata_order(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("function mountAppShell()", source)
        for view_id in ("view-home", "view-slide", "view-jump", "view-settings"):
            self.assertIn(f'id="{view_id}"', source)
        updated = source.index('id="guide-updated"')
        target = source.index('id="guide-target"')
        self.assertLess(updated, target)
        self.assertIn('class="guide-meta"', source)

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

    def test_browser_history_tracks_screens_and_replaces_route_steps(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('writeNavigation({ view: "home" }, "replace");', source)
        self.assertIn('window.addEventListener("popstate"', source)
        self.assertIn('view: "transition"', source)
        self.assertIn('view: "jump"', source)
        self.assertIn('writeNavigation({ view: "settings" });', source)
        self.assertIn('}, "replace");', source)
        self.assertIn("history.back();", source)

    def test_route_history_preserves_transition_parent_across_steps(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            'fromView: options.fromView || currentNavigation().view || "home"',
            source,
        )
        self.assertGreaterEqual(
            source.count('fromView: currentNavigation().fromView || null'),
            2,
        )
        self.assertIn(
            'if (currentNavigation().fromView === "transition")',
            source,
        )

    def test_settings_back_uses_browser_history(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('onclick="closeSettings()"', source)
        self.assertIn(
            "function closeSettings() {\n  history.back();\n}",
            source,
        )

    def test_route_cards_share_uniform_minimum_height(self):
        source = STYLE.read_text(encoding="utf-8")
        self.assertIn("min-height: 90px;", source)
        self.assertNotIn("\n  height: 90px;\n  min-height: 90px;", source)


if __name__ == "__main__":
    unittest.main()

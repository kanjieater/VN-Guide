import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "guide-app.js"
STYLE = ROOT / "style.css"


class SharedGuideUiTests(unittest.TestCase):
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

    def test_route_cards_have_fixed_uniform_height(self):
        source = STYLE.read_text(encoding="utf-8")
        self.assertIn("height: 90px;", source)
        self.assertIn("min-height: 90px;", source)


if __name__ == "__main__":
    unittest.main()

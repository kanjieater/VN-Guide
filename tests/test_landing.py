import unittest
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "scripts" / "templates" / "landing.html"


class LandingPlayingFilterTests(unittest.TestCase):
    def test_playing_filter_requires_visible_nonzero_progress(self):
        source = LANDING.read_text(encoding="utf-8")
        self.assertIn(
            "const pct = maxProgress ? Math.round(doneSteps / maxProgress * 100) : 0;",
            source,
        )
        self.assertIn("return pct > 0 && pct < 100;", source)

    def test_filters_share_one_control_row(self):
        source = LANDING.read_text(encoding="utf-8")
        start = source.index('<div class="control-row">')
        end = source.index('<input id="search"', start)
        row = source[start:end]
        self.assertNotIn("<br>", row)
        for button_id in ("btn-recent", "btn-alpha", "btn-all", "btn-playing"):
            self.assertIn(f'id="{button_id}"', row)

    def test_storage_key_uses_canonical_encoded_guide_url(self):
        source = LANDING.read_text(encoding="utf-8")
        self.assertIn(
            'new URL(`./${encodeURIComponent(slug)}/`, location.href).pathname',
            source,
        )

        slug = "マブラヴ-altered-fable"
        browser_pathname = f"/{quote(slug, safe='')}/"
        expected_key = "guide_" + browser_pathname.replace("/", "_")
        raw_key = "guide_" + f"/{slug}/".replace("/", "_")

        self.assertIn("%E3%83%9E", expected_key)
        self.assertNotEqual(expected_key, raw_key)


if __name__ == "__main__":
    unittest.main()

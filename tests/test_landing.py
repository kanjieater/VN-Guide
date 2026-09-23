import unittest
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "scripts" / "templates" / "landing.html"


class LandingPlayingFilterTests(unittest.TestCase):
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

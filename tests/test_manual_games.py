import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


guide_gen = load_module("vn_guide_gen_manual_games", ROOT / "scripts" / "guide_gen.py")
generate = load_module("vn_generate_manual_games", ROOT / "scripts" / "generate.py")


class ManualGameIsolationTests(unittest.TestCase):
    def test_guide_gen_ignores_namespaced_non_vn_game(self):
        with tempfile.TemporaryDirectory() as td:
            games_json = Path(td) / "games.json"
            games_json.write_text(
                json.dumps(
                    {
                        "game:black-matrix-oo": {
                            "slug": "black-matrix-oo",
                            "title": "BLACK/MATRIX OO",
                            "has_guide": False,
                            "guide_target": {
                                "label": "BLACK/MATRIX OO (2004 original)",
                                "platform": "PlayStation",
                                "url": "https://example.com/black-matrix-oo",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(guide_gen, "GAMES_JSON", games_json),
                patch.object(
                    guide_gen.agent_runner,
                    "credentials_available",
                    return_value=True,
                ),
                patch.object(guide_gen, "generate_guide") as generate_guide,
            ):
                guide_gen.run()

            generate_guide.assert_not_called()

    def test_generate_does_not_query_vndb_for_manual_game_cover(self):
        with tempfile.TemporaryDirectory() as td:
            games_json = Path(td) / "games.json"
            games_json.write_text(
                json.dumps(
                    {
                        "game:black-matrix-oo": {
                            "slug": "black-matrix-oo",
                            "title": "BLACK/MATRIX OO",
                            "alttitle": "ブラックマトリクス ダブルオー",
                            "cover_url": "",
                            "has_guide": False,
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(generate, "GAMES_JSON", games_json),
                patch.object(generate.pull_vndb, "fetch_playing_list", return_value=[]),
                patch.object(generate.pull_vndb, "lookup_vn_by_id") as lookup,
                patch.object(generate, "scaffold_guide"),
                patch.object(generate, "generate_landing"),
            ):
                generate.run()

            lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()

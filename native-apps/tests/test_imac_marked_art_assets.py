"""Guard recovered, approved iMac screen artwork in the native release."""
import unittest
from pathlib import Path
from eden_native.home_categories import HOME_CATEGORIES

ASSETS = Path(__file__).resolve().parents[1] / "assets"


class ImacMarkedArtworkTests(unittest.TestCase):
    def test_every_play_learn_create_card_uses_original_imac_asset(self):
        missing = [
            name for activities in HOME_CATEGORIES.values() for name in activities
            if not (ASSETS / "imac-activity-cards" / (name + ".png")).is_file()
        ]
        # My Day is a composite activity without an installed single activity-art card.
        self.assertEqual(missing, ["my-day"])

    def test_approved_story_shelf_art_is_present(self):
        reader = ASSETS / "stories" / "imac-reader"
        for name in ("choose-story-banner-v27.png", "choose-story-wood-v26.png",
                     "reader-backdrop-flat-v108.png"):
            with self.subTest(name=name):
                self.assertGreater((reader / name).stat().st_size, 5000)

    def test_original_story_page_art_is_preserved(self):
        pages = list((ASSETS / "stories" / "imac-page-art").rglob("page-*.png"))
        pages += list((ASSETS / "stories" / "imac-page-art").rglob("page-*.jpg"))
        self.assertGreaterEqual(len(pages), 140)


if __name__ == "__main__":
    unittest.main()

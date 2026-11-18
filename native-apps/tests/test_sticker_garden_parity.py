"""iMac-equivalent sticker placement persistence and safety rules."""
import tempfile
import unittest
from pathlib import Path
from eden_native.sticker_garden import SLOTS, load_garden, save_garden


class StickerGardenParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "eden" / "sticker-garden.json"
        self.allowed = {"butterfly", "flower"}

    def tearDown(self):
        self.temp.cleanup()

    def test_imac_six_by_four_board_and_round_trip(self):
        self.assertEqual(SLOTS, 24)
        save_garden(self.path, {0: "butterfly", 23: "flower"}, self.allowed)
        self.assertEqual(load_garden(self.path, self.allowed), {0: "butterfly", 23: "flower"})

    def test_unapproved_stickers_and_invalid_slots_rejected(self):
        for placements in ({0: "unapproved"}, {-1: "butterfly"}, {SLOTS: "flower"}):
            with self.subTest(placements=placements), self.assertRaises(ValueError):
                save_garden(self.path, placements, self.allowed)

    def test_child_files_are_separate_and_stale_unlocks_not_loaded(self):
        other = Path(self.temp.name) / "colby" / "sticker-garden.json"
        save_garden(self.path, {0: "butterfly"}, self.allowed)
        save_garden(other, {1: "flower"}, self.allowed)
        self.assertEqual(load_garden(other, self.allowed), {1: "flower"})
        self.assertEqual(load_garden(self.path, {"flower"}), {})

    def test_corrupt_or_duplicated_slots_fail_closed(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text('{"version":1,"placements":[{"slot":2,"sku":"flower"},{"slot":2,"sku":"butterfly"}]}')
        self.assertEqual(load_garden(self.path, self.allowed), {})


if __name__ == "__main__":
    unittest.main()

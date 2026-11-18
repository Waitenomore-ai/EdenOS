"""iMac-equivalent sticker placement persistence and safety rules."""
import tempfile
import unittest
from pathlib import Path
from eden_native.garden_stars import GardenStars
from eden_native.sticker_garden import StickerGarden, STICKERS, FREE_STICKERS, MAX_PLACEMENTS


class StickerGardenParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'garden-stars.sqlite3'
        self.rewards = GardenStars(self.db)
        for child in ('eden', 'colby'):
            self.rewards.create_profile(child)
        self.garden = StickerGarden(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_75_stickers_and_40_placement_limit(self):
        self.assertEqual(len(STICKERS), 75)
        self.assertEqual(MAX_PLACEMENTS, 40)
        self.assertTrue(FREE_STICKERS.issubset(STICKERS))

    def test_unlocked_sticker_is_child_scoped_and_can_move_and_remove(self):
        paid = next(sku for sku in sorted(STICKERS) if sku not in FREE_STICKERS)
        self.rewards.unlock('eden', paid, parent_authorized=True)
        placement = self.garden.place('eden', paid, 0.1, 0.2)
        self.assertEqual(len(self.garden.list_placements('eden')), 1)
        self.assertEqual(self.garden.list_placements('colby'), [])
        with self.assertRaises(PermissionError):
            self.garden.place('colby', paid, 0.3, 0.4)
        self.garden.move('eden', placement, 0.5, 0.6)
        self.assertEqual(self.garden.list_placements('eden')[0]['x'], 0.5)
        with self.assertRaises(LookupError):
            self.garden.remove('colby', placement)
        self.garden.remove('eden', placement)
        self.assertEqual(self.garden.list_placements('eden'), [])

    def test_bad_coordinates_and_occupied_space_rejected(self):
        free = next(iter(FREE_STICKERS))
        placed = self.garden.place('eden', free, 0.2, 0.3)
        with self.assertRaises(ValueError):
            self.garden.place('eden', free, 0.2, 0.3)
        with self.assertRaises(ValueError):
            self.garden.move('eden', placed, 2.0, 0.3)

if __name__ == '__main__':
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from eden_native.wallpaper_choices import WallpaperChoices


class WallpaperChoicesTests(unittest.TestCase):
    def test_selection_is_child_scoped_and_persistent(self):
        with tempfile.TemporaryDirectory() as folder:
            store = WallpaperChoices(Path(folder) / 'wallpapers.json')
            self.assertTrue(store.choose('eden', 'garden.png', {'garden.png', 'meadow.png'}))
            self.assertEqual(store.selected('eden', {'garden.png'}), 'garden.png')
            self.assertIsNone(store.selected('colby', {'garden.png'}))
            self.assertEqual(WallpaperChoices(store.path).selected('eden', {'garden.png'}), 'garden.png')
            self.assertTrue(store.choose('colby', 'meadow.png', {'garden.png', 'meadow.png'}))
            self.assertEqual(store.selected('eden', {'garden.png', 'meadow.png'}), 'garden.png')

    def test_rejects_unapproved_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            store = WallpaperChoices(Path(folder) / 'wallpapers.json')
            self.assertFalse(store.choose('../eden', 'garden.png', {'garden.png'}))
            self.assertFalse(store.choose('eden', '../../private.png', {'garden.png'}))
            self.assertFalse(store.choose('eden', 'unapproved.png', {'garden.png'}))
            self.assertIsNone(store.selected('eden', {'garden.png'}))

    def test_corrupt_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'wallpapers.json'
            path.write_text('not-json', encoding='utf-8')
            self.assertIsNone(WallpaperChoices(path).selected('eden', {'garden.png'}))

if __name__ == '__main__':
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from eden_native.sticker_garden import load_garden, save_garden


class StickerGardenStorageTests(unittest.TestCase):
    def test_save_load_and_child_file_isolation(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / 'eden.json'
            second = Path(folder) / 'other.json'
            allowed = {'sticker_apple'}
            save_garden(first, {0: 'sticker_apple', 11: 'sticker_apple'}, allowed)
            self.assertEqual(load_garden(first, allowed), {0: 'sticker_apple', 11: 'sticker_apple'})
            self.assertEqual(load_garden(second, allowed), {})
            self.assertEqual(load_garden(first, set()), {})

    def test_invalid_replacement_cannot_overwrite_garden(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'eden.json'
            save_garden(path, {0: 'sticker_apple'}, {'sticker_apple'})
            original = path.read_bytes()
            for placements in ({24: 'sticker_apple'}, {0: 'sticker_locked'}, {True: 'sticker_apple'}):
                with self.assertRaises(ValueError):
                    save_garden(path, placements, {'sticker_apple'})
                self.assertEqual(path.read_bytes(), original)
            path.write_text('{bad-json')
            self.assertEqual(load_garden(path, {'sticker_apple'}), {})

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'target.json'
            target.write_text('private')
            link = Path(folder) / 'eden.json'
            link.symlink_to(target)
            self.assertEqual(load_garden(link, {'sticker_apple'}), {})
            with self.assertRaises(ValueError):
                save_garden(link, {0: 'sticker_apple'}, {'sticker_apple'})
            self.assertEqual(target.read_text(), 'private')

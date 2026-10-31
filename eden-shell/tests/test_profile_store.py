import os
import tempfile
import unittest
from pathlib import Path

from eden_shell.profile_cards import make_profile_card
from eden_shell.profile_store import load_profiles, remove_profile, save_profiles


class ProfileStoreTests(unittest.TestCase):
    def test_round_trip_stores_only_greeter_metadata_and_restricts_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            save_profiles([make_profile_card("sam", "Sam", "butterfly")], path)
            self.assertEqual(load_profiles(path)[0].display_name, "Sam")
            self.assertIn('"avatar": "butterfly"', path.read_text(encoding="utf-8"))
            self.assertEqual(os.stat(path).st_mode & 0o077, 0)

    def test_invalid_or_duplicate_records_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text('{"profiles":[{"username":"sam","display_name":"Sam","avatar":"../x"}]}', encoding="utf-8")
            self.assertEqual(load_profiles(path), ())
            with self.assertRaises(ValueError):
                save_profiles(
                    [make_profile_card("sam", "Sam", "sun"), make_profile_card("sam", "Sam again", "moon")],
                    path,
                )

    def test_remove_profile_resets_one_child_without_touching_others(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            save_profiles(
                [make_profile_card("sam", "Sam", "sun"), make_profile_card("lee", "Lee", "tree")],
                path,
            )
            self.assertTrue(remove_profile("sam", path))
            self.assertEqual([card.username for card in load_profiles(path)], ["lee"])
            self.assertFalse(remove_profile("missing", path))


if __name__ == "__main__":
    unittest.main()

"""Only synthetic child accounts: never read a real profile during CI."""
import json
import tempfile
import unittest
from pathlib import Path

from native_eden_v0.eden_core.profile_source import read_profile_cards


class ProfileSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "profiles.json"

    def write(self, records):
        self.path.write_text(json.dumps({"profiles": records}), encoding="utf-8")

    def test_reads_existing_imac_card_format_without_writing(self):
        self.write([
            {"username": "sample_one", "display_name": "Sample One", "avatar": "approved-eden"},
            {"username": "sample_two", "display_name": "Sample Two", "avatar": "approved-mila"}
        ])
        original = self.path.read_bytes()
        cards = read_profile_cards(self.path)
        self.assertEqual([c.display_name for c in cards], ["Sample One", "Sample Two"])
        self.assertEqual(cards[1].avatar, "approved-mila")
        self.assertEqual(self.path.read_bytes(), original)

    def test_missing_file_does_not_create_default_accounts(self):
        self.assertEqual(read_profile_cards(self.path), ())
        self.assertFalse(self.path.exists())

    def test_invalid_or_duplicate_cards_fail_closed(self):
        self.write([
            {"username": "same", "display_name": "One", "avatar": "approved-eden"},
            {"username": "same", "display_name": "Two", "avatar": "approved-mila"}
        ])
        self.assertEqual(read_profile_cards(self.path), ())
        self.write([{"username": "one", "display_name": "One", "avatar": "../../secret"}])
        self.assertEqual(read_profile_cards(self.path), ())


if __name__ == "__main__":
    unittest.main()

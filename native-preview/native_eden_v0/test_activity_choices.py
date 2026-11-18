"""Synthetic tests for iMac-compatible per-child activity restrictions."""
import json
import tempfile
import unittest
from pathlib import Path

from .eden_core.activity_choices import read_choices, save_choices


class ActivityChoicesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.known = ("sample_child",)
    def tearDown(self):
        self.tmp.cleanup()

    def test_existing_imac_format_is_read_only(self):
        p = self.root / "activity-choices" / "sample_child.json"
        p.parent.mkdir()
        p.write_text(json.dumps({"version": 1, "enabled": {"art-studio": False, "story-garden": True}}))
        before = p.read_bytes()
        self.assertEqual(read_choices(self.root, "sample_child", self.known),
                         {"art-studio": False, "story-garden": True})
        self.assertEqual(p.read_bytes(), before)

    def test_unrecognised_child_does_not_load_or_write(self):
        self.assertEqual(read_choices(self.root, "../escape", self.known), {})
        with self.assertRaises(ValueError):
            save_choices(self.root, "../escape", {}, self.known, parent_unlocked=True)

    def test_parent_pin_required_for_persisting_restrictions(self):
        with self.assertRaises(PermissionError):
            save_choices(self.root, "sample_child", {"art-studio": False}, self.known, parent_unlocked=False)
        self.assertFalse((self.root / "activity-choices").exists())

    def test_parent_can_save_and_reload_approved_activity_only(self):
        save_choices(self.root, "sample_child", {"art-studio": False}, self.known, parent_unlocked=True)
        self.assertEqual(read_choices(self.root, "sample_child", self.known), {"art-studio": False})
        self.assertEqual((self.root / "activity-choices" / "sample_child.json").stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError):
            save_choices(self.root, "sample_child", {"unreviewed-game": True}, self.known, parent_unlocked=True)

    def test_malformed_and_incorrect_version_fail_closed(self):
        p = self.root / "activity-choices" / "sample_child.json"
        p.parent.mkdir()
        p.write_text('{"version":2,"enabled":{"art-studio":false}}')
        self.assertEqual(read_choices(self.root, "sample_child", self.known), {})
        p.write_text('{"version":1,"enabled":{"art-studio":"no"}}')
        self.assertEqual(read_choices(self.root, "sample_child", self.known), {})


if __name__ == "__main__":
    unittest.main()

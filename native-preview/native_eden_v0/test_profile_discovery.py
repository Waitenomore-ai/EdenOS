"""Local profile discovery must never create, migrate or copy accounts."""
import json
import tempfile
import unittest
from pathlib import Path

from .eden_core.profile_discovery import find_existing_profiles


class ProfileDiscoveryTests(unittest.TestCase):
    def test_valid_existing_profiles_detected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / ".config" / "eden-os" / "profiles.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"profiles": [
                {"username": "synthetic_child", "display_name": "Sample", "avatar": "approved-eden"}
            ]}))
            before = path.read_bytes()
            self.assertEqual(find_existing_profiles(root), path)
            self.assertEqual(path.read_bytes(), before)

    def test_absent_profiles_are_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(find_existing_profiles(root))
            self.assertFalse((root / ".config").exists())

    def test_invalid_profiles_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / ".config" / "eden-os" / "profiles.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"profiles":[{"username":"bad","display_name":"Bad","avatar":"unapproved"}]}')
            self.assertIsNone(find_existing_profiles(root))


if __name__ == "__main__":
    unittest.main()

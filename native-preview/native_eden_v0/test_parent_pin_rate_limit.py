"""Regression tests for persistent Parent Corner PIN attempt throttling."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_eden_v0.eden_core import parent_pin


class ParentPinRateLimitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, {"XDG_CONFIG_HOME": self.tmp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        parent_pin.set_pin("2468")

    def test_five_failures_lock_even_the_correct_pin(self):
        with patch("time.time", return_value=1000):
            for _ in range(5):
                self.assertFalse(parent_pin.verify_pin("0000"))
            self.assertFalse(parent_pin.verify_pin("2468"))

    def test_lock_expires_and_correct_pin_resets_failures(self):
        with patch("time.time", return_value=1000):
            for _ in range(5):
                self.assertFalse(parent_pin.verify_pin("0000"))
        with patch("time.time", return_value=1061):
            self.assertTrue(parent_pin.verify_pin("2468"))
            for _ in range(4):
                self.assertFalse(parent_pin.verify_pin("0000"))
            self.assertTrue(parent_pin.verify_pin("2468"))

    def test_attempt_state_is_private_and_persistent(self):
        with patch("time.time", return_value=1000):
            for _ in range(5):
                parent_pin.verify_pin("0000")
            self.assertFalse(parent_pin.verify_pin("2468"))
        state = Path(self.tmp.name) / "eden-os" / "parent-pin-attempts.json"
        self.assertTrue(state.exists())
        self.assertEqual(state.stat().st_mode & 0o777, 0o600)

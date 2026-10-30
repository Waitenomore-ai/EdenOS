"""Check launcher preference persistence without a display server.

GTK is stubbed only to import the window class; the window callback and
filesystem persistence run unchanged.
"""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from eden_shell.preferences import AccessibilityPreferences, load_preferences


def load_window_class():
    gi = ModuleType('gi')
    gi.require_version = lambda *_: None
    repository = ModuleType('gi.repository')
    repository.Gtk = SimpleNamespace(ApplicationWindow=object, Application=object)
    repository.Gio = SimpleNamespace()
    repository.GLib = SimpleNamespace()
    path = Path(__file__).resolve().parents[1] / 'eden_shell' / 'app.py'
    spec = importlib.util.spec_from_file_location('eden_shell._preference_test_app', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'gi': gi, 'gi.repository': repository}):
        spec.loader.exec_module(module)
    return module.EdenWindow


class WindowState:
    def __init__(self):
        self.preferences = AccessibilityPreferences()
        self.messages = []
        self.rendered_preferences = None

    def _show_status(self, message):
        self.messages.append(message)

    def _apply_preferences(self):
        self.rendered_preferences = self.preferences

    def _update(self):
        pass


class PreferenceErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.window_class = load_window_class()

    def test_failed_save_preserves_current_settings_and_reports_failure(self):
        window = WindowState()
        requested = AccessibilityPreferences(1.4, True, True)
        with tempfile.TemporaryDirectory() as directory:
            blocker = Path(directory) / 'not-a-directory'
            blocker.write_text('existing file')
            with patch.dict(os.environ, {'XDG_CONFIG_HOME': str(blocker)}):
                try:
                    self.window_class._store_preferences(window, requested)
                except OSError as exc:
                    self.fail(f'Save failures must be shown in the launcher: {exc}')
            self.assertEqual(blocker.read_text(), 'existing file')
        self.assertEqual(window.preferences, AccessibilityPreferences())
        self.assertTrue(window.messages)
        self.assertIn('save', window.messages[-1].lower())

    def test_successful_save_updates_display_and_persistent_preferences(self):
        window = WindowState()
        requested = AccessibilityPreferences(1.4, True, True)
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'XDG_CONFIG_HOME': directory}):
                self.window_class._store_preferences(window, requested)
                self.assertEqual(load_preferences(), requested)
        self.assertEqual(window.preferences, requested)
        self.assertEqual(window.rendered_preferences, requested)
        self.assertEqual(window.messages, [])

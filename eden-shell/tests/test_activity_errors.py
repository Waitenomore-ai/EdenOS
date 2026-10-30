"""Missing desktop metadata must produce a message, not escape the GTK callback."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from eden_shell.catalogue import Activity
from test_preference_errors import load_window_class


class ActivityErrorTests(unittest.TestCase):
    def test_missing_desktop_constructor_error_is_handled(self):
        window_class = load_window_class()
        messages = []
        window = SimpleNamespace(_show_status=messages.append)
        activity = Activity('missing', 'Missing', '', 'create', 'missing.desktop', True)
        def missing(_desktop_id):
            raise TypeError('constructor returned NULL')
        globals_ = window_class._launch_activity.__globals__
        with patch.dict(globals_, {
            'Gio': SimpleNamespace(DesktopAppInfo=SimpleNamespace(new=missing)),
            'GLib': SimpleNamespace(Error=RuntimeError),
        }):
            try:
                window_class._launch_activity(window, activity)
            except TypeError as exc:
                self.fail(f'Missing activities must show a help message: {exc}')
        self.assertEqual(len(messages), 1)
        self.assertIn('adult', messages[0])

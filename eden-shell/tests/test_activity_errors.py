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

    def test_double_click_launches_once(self):
        from eden_shell.launch_control import LaunchCooldown
        window_class = load_window_class()
        messages, launches = [], []
        window = SimpleNamespace(_show_status=messages.append,
                                 _launch_cooldown=LaunchCooldown(clock=lambda:10.0))
        activity = Activity('paint', 'Paint', '', 'create', 'paint.desktop', True)
        info = SimpleNamespace(launch=lambda *_:launches.append('paint'))
        with patch.dict(window_class._launch_activity.__globals__, {
            'Gio': SimpleNamespace(DesktopAppInfo=SimpleNamespace(new=lambda _:info)),
            'GLib': SimpleNamespace(Error=RuntimeError),
        }):
            window_class._launch_activity(window, activity)
            window_class._launch_activity(window, activity)
        self.assertEqual(launches, ['paint'])
        self.assertIn('moment', messages[-1])

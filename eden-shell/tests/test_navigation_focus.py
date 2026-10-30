from types import SimpleNamespace
import unittest
from test_preference_errors import load_window_class


class NavigationFocusTests(unittest.TestCase):
    def test_navigation_can_focus_page_without_forcing_focus_on_other_updates(self):
        window_class = load_window_class()
        focused = []
        target = SimpleNamespace(grab_focus=lambda:focused.append('page'))
        window = SimpleNamespace(_render=lambda:None, _page_focus_target=target)
        try:
            window_class._update(window, focus_page=True)
        except TypeError as exc:
            self.fail(f'Navigation needs explicit page focus: {exc}')
        self.assertEqual(focused, ['page'])
        window_class._update(window)
        self.assertEqual(focused, ['page'])

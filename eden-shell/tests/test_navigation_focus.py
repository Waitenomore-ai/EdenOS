from pathlib import Path
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


class HomeActivityReachabilityTests(unittest.TestCase):
    def test_explore_opens_read_category_for_story_garden(self):
        source = (Path(__file__).resolve().parents[1] / "eden_shell" / "app.py").read_text()
        self.assertIn('("Explore", "explore", self._open_category("read"), True, "explore")', source)


class CompactHomeAndGameExitTests(unittest.TestCase):
    def test_home_greeting_and_prompt_do_not_expand_across_screen(self):
        source = (Path(__file__).resolve().parents[1] / "eden_shell" / "app.py").read_text()
        self.assertIn("welcome.set_halign(Gtk.Align.START)", source)
        self.assertIn("prompt.set_halign(Gtk.Align.START)", source)
        self.assertIn("welcome.set_hexpand(False)", source)
        self.assertIn("prompt.set_hexpand(False)", source)

    def test_all_eight_games_have_a_clear_back_home_control(self):
        root = Path(__file__).resolve().parents[1] / "eden_shell"
        for name in ("number_meadow", "word_woodland", "story_garden",
                     "art_studio", "puzzle_pond", "time_routines",
                     "nature_explorer", "feelings"):
            with self.subTest(name=name):
                source = (root / (name + ".py")).read_text()
                self.assertIn('label="← Back to Eden Home"', source)
                self.assertIn('back_home.connect("clicked", lambda _button: self.close())', source)

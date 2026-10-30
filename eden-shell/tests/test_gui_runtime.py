"""Real GTK checks, opt-in under Xvfb on the Debian build host."""
import os
import tempfile
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('EDEN_GUI_TESTS') == '1', 'Needs Debian GTK runtime and display')
class GtkRuntimeTests(unittest.TestCase):
    def test_navigation_accessibility_controls_and_adult_setup_construct(self):
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import GLib, Gtk
        from eden_shell.app import EdenApplication, EdenWindow
        from eden_shell.catalogue import Activity
        from eden_shell.setup import SetupApplication, SetupWindow
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'XDG_CONFIG_HOME': directory}):
                app = EdenApplication()
                self.assertTrue(app.register(None))
                window = EdenWindow(app)
                window.present()
                context = GLib.MainContext.default()
                for _ in range(50):
                    if context.pending():
                        context.iteration(False)
                self.assertIsNotNone(window.get_child())
                self.assertEqual(window.get_focus(), window._page_focus_target)
                window._open_category('create')(None)
                self.assertEqual(window.state.category, 'create')
                self.assertEqual(window.get_focus().get_label(), 'Home')
                window._launch_activity(Activity('missing', 'Missing', 'Unavailable fixture',
                                                 'create', 'eden-does-not-exist.desktop', True))
                self.assertIn("couldn't open", window._status_label.get_text())
                status_label = window._status_label
                window._launch_activity(Activity('missing', 'Missing', 'Unavailable fixture',
                                                 'create', 'eden-does-not-exist.desktop', True))
                self.assertIs(window._status_label, status_label)
                window._open_settings(None)
                for _ in range(6):
                    window._bigger_text(None)
                self.assertEqual(window.preferences.text_scale, 1.6)
                window._toggle_high_contrast(None)
                self.assertTrue(window.has_css_class('contrast'))
                window._go_home(None)
                self.assertEqual(window.state.page, 'home')
                self.assertEqual(window.get_focus(), window._page_focus_target)
                window.destroy()
                app.quit()
                setup = SetupApplication()
                self.assertTrue(setup.register(None))
                with patch('eden_shell.setup.is_live_session', return_value=True):
                    setup_window = SetupWindow(setup)
                self.assertIsNotNone(setup_window.get_child())
                widgets = [setup_window.get_child()]
                labels = []
                while widgets:
                    widget = widgets.pop()
                    if isinstance(widget, Gtk.Label):
                        labels.append(widget.get_text())
                    child = widget.get_first_child()
                    while child is not None:
                        widgets.append(child)
                        child = child.get_next_sibling()
                self.assertTrue(any('live USB session' in label for label in labels))
                setup_window.destroy()
                setup.quit()


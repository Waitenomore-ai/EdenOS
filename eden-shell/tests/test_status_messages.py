from types import SimpleNamespace
import unittest
from unittest.mock import patch
from test_preference_errors import load_window_class


class StatusMessageTests(unittest.TestCase):
    def test_repeated_messages_replace_one_status_row(self):
        window_class = load_window_class()
        class Label:
            def __init__(self, label):
                self.text = label
            def add_css_class(self, value): pass
            def set_wrap(self, value): pass
            def set_xalign(self, value): pass
            def set_label(self, value): self.text = value
        class Box:
            def __init__(self): self.children = []
            def append(self, value): self.children.append(value)
        box = Box()
        window = SimpleNamespace(get_child=lambda:box)
        with patch.dict(window_class._show_status.__globals__,
                        {'Gtk':SimpleNamespace(Label=Label,Box=Box)}):
            for index in range(10):
                window_class._show_status(window, f'Unavailable activity {index}')
        self.assertEqual(len(box.children), 1)
        self.assertEqual(box.children[0].text, 'Unavailable activity 9')

    def test_shutdown_dialog_cannot_close_while_request_is_pending(self):
        window_class = load_window_class()
        method = getattr(window_class, '_close_power_off_dialog', None)
        self.assertTrue(callable(method), 'Pending shutdown needs a close guard')
        self.assertTrue(method(SimpleNamespace(_shutdown_pending=True), None))
        self.assertFalse(method(SimpleNamespace(_shutdown_pending=False), None))

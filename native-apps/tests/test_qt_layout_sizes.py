"""Basic small-screen regression tests; not a substitute for physical-device QA."""
import tempfile, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE = Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_small_screen_navigation_and_studio_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            platform = detect_platform('linux', Path(tmp), {'XDG_DATA_HOME':tmp+'/data', 'XDG_CONFIG_HOME':tmp+'/config'})
            repo = ProfileRepository(platform)
            repo.create('layout_child','Layout Child','approved-eden')
            pin = ApprovedPinAdapter(platform, SOURCE)
            pin.set_pin('2468')
            window = create_window(pin_adapter=pin, profiles=repo)
            window.resize(800, 600)
            window.show()
            self.app.processEvents()
            try:
                self.assertLessEqual(window.width(), 800)
                for label in ('Layout Child', 'Art Studio'):
                    buttons = [b for b in window.controls_widget.findChildren(QPushButton) if b.text() == label]
                    self.assertEqual(len(buttons), 1)
                    buttons[0].click()
                    self.app.processEvents()
                self.assertEqual(window.state.page, 'art-studio')
                self.assertTrue(window.art_canvas.isVisible())
                labels = {b.text() for b in window.controls_widget.findChildren(QPushButton)}
                self.assertTrue({'Save editable drawing', 'Open saved drawing', 'Eraser', 'Small brush', 'Medium brush', 'Large brush'}.issubset(labels))
                self.assertTrue(window.scroll_area.verticalScrollBar().maximum() >= 0)
            finally:
                window.close()
                self.app.processEvents()

import tempfile, unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE = Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class AccessibilitySmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_keyboard_navigation_and_accessible_canvas(self):
        with tempfile.TemporaryDirectory() as tmp:
            platform = detect_platform("linux", Path(tmp), {"XDG_DATA_HOME": tmp+"/data", "XDG_CONFIG_HOME": tmp+"/config"})
            repo = ProfileRepository(platform)
            repo.create("eden_demo", "Eden Demo", "approved-eden")
            pin = ApprovedPinAdapter(platform, SOURCE)
            pin.set_pin("1234")
            window = create_window(pin_adapter=pin, profiles=repo)
            window.resize(800, 600)
            window.show()
            self.app.processEvents()
            try:
                profile = next(b for b in window.controls_widget.findChildren(QPushButton) if b.text() == "Eden Demo")
                profile.setFocus()
                QTest.keyClick(profile, Qt.Key.Key_Space)
                self.app.processEvents()
                self.assertEqual(window.state.page, "home")
                create = next(b for b in window.controls_widget.findChildren(QPushButton) if b.accessibleName() == "Create")
                create.setFocus()
                QTest.keyClick(create, Qt.Key.Key_Space)
                self.app.processEvents()
                art = next(b for b in window.controls_widget.findChildren(QPushButton) if b.text() == "Art Studio")
                art.setFocus()
                QTest.keyClick(art, Qt.Key.Key_Space)
                self.app.processEvents()
                self.assertEqual(window.state.page, "art-studio")
                self.assertEqual(window.art_canvas.accessibleName(), "Art Studio drawing canvas")
                self.assertTrue(window.scroll_area.isVisible())
            finally:
                window.close()
                self.app.processEvents()

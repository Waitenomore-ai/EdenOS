"""Check the iMac-inspired centred activity heading and persistent Home control."""
import tempfile, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE = Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class SharedToolbarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def test_activity_has_central_heading_and_home_navigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            platform=detect_platform('linux',Path(tmp),{'XDG_DATA_HOME':tmp+'/data','XDG_CONFIG_HOME':tmp+'/config'})
            repo=ProfileRepository(platform)
            repo.create('toolbar_child','Toolbar Child','approved-eden')
            pin=ApprovedPinAdapter(platform,SOURCE)
            pin.set_pin('2468')
            window=create_window(pin_adapter=pin,profiles=repo)
            window.resize(800,600)
            window.show();self.app.processEvents()
            try:
                self.assertFalse(window.activity_toolbar.isVisible())
                for label in ('Toolbar Child','Art Studio'):
                    buttons=[b for b in window.controls_widget.findChildren(QPushButton) if (b.text()==label or b.accessibleName()==label)]
                    self.assertEqual(len(buttons),1)
                    buttons[0].click();self.app.processEvents()
                self.assertTrue(window.activity_toolbar.isVisible())
                self.assertEqual(window.toolbar_heading.text(),'Art Studio')
                self.assertEqual(window.toolbar_home.accessibleName(),'Home')
                self.assertTrue(window.toolbar_home.isVisible())
                window.toolbar_home.click();self.app.processEvents()
                self.assertEqual(window.state.page,'home')
                self.assertFalse(window.activity_toolbar.isVisible())
            finally:
                window.close();self.app.processEvents()

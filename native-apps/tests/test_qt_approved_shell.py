"""Approved native visual shell regression checks."""
import unittest
from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from eden_native.qt_app import create_window


class ApprovedShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_login_uses_approved_banner_and_portrait(self):
        from eden_native.core import detect_platform
        from eden_native.profiles import ProfileRepository
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory(prefix="eden-shell-") as folder:
            platform = detect_platform("linux", Path(folder), {"XDG_DATA_HOME": folder + "/data", "XDG_CONFIG_HOME": folder + "/config"})
            profiles = ProfileRepository(platform)
            profiles.create("eden", "Eden", "approved-eden")
            window = create_window(profiles=profiles)
            window.show()
            self.app.processEvents()
            self.assertIn("#e9f5e8", window.styleSheet())
            banner = window.findChild(QLabel, "edenApprovedLoginBanner")
            self.assertIsNotNone(banner)
            self.assertFalse(banner.pixmap().isNull())
            buttons = [b for b in window.findChildren(QPushButton) if b.text() == "Eden"]
            self.assertEqual(len(buttons), 1)
            self.assertFalse(buttons[0].icon().isNull())
            window.close()


if __name__ == "__main__":
    unittest.main()

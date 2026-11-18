"""Structural iMac Art Studio layout checks; not a visual sign-off."""
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton, QScrollArea, QWidget
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE = Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class ArtLayoutParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_approved_sidebar_canvas_and_toolbar_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            platform = detect_platform('linux', Path(tmp), {'XDG_DATA_HOME':tmp+'/data', 'XDG_CONFIG_HOME':tmp+'/config'})
            repo = ProfileRepository(platform)
            repo.create('layout_parity_child','Layout Parity Child','approved-eden')
            pin = ApprovedPinAdapter(platform, SOURCE)
            pin.set_pin('2468')
            window = create_window(pin_adapter=pin, profiles=repo)
            window.resize(1280, 900)
            window.show()
            self.app.processEvents()
            try:
                for label in ('Layout Parity Child','Create','Art Studio'):
                    matches=[b for b in window.controls_widget.findChildren(QPushButton) if (b.text()==label or b.accessibleName()==label)]
                    self.assertEqual(len(matches),1,label)
                    matches[0].click()
                    self.app.processEvents()
                scene=window.controls_widget.findChild(QWidget,'edenArtStudioScene')
                self.assertIsNotNone(scene)
                sidebar=scene.findChild(QScrollArea,'edenArtStudioSidebar')
                self.assertIsNotNone(sidebar)
                self.assertEqual(sidebar.width(),260)
                self.assertIsNotNone(scene.findChild(QWidget,'edenArtStudioWorkspace'))
                self.assertIsNotNone(scene.findChild(QWidget,'edenArtStudioActions'))
                self.assertIsNotNone(scene.findChild(QWidget,'edenArtStudioDock'))
                self.assertIsNotNone(scene.findChild(QWidget,'edenArtStudioWallpaperPicker'))
                self.assertTrue(window.art_canvas.isVisible())
                labels={b.text() for b in scene.findChildren(QPushButton)}
                self.assertTrue({'Pen','Pencil','Crayon','Paint','Eraser','Sky','Grass','Peach','White','Save editable drawing','Open saved drawing'}.issubset(labels))
                sky=[b for b in scene.findChildren(QPushButton) if b.text()=='Sky']
                self.assertEqual(len(sky),1)
                sky[0].click()
                self.assertEqual(window.art_canvas.background.name(),'#e4f2ff')
            finally:
                window.close()
                self.app.processEvents()

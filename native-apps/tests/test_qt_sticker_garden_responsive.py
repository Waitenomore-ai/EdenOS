import unittest
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from pathlib import Path
import tempfile

class StickerGardenResponsiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def test_garden_fits_width_at_compact_and_full_hd_sizes(self):
  with tempfile.TemporaryDirectory() as folder:
   platform=detect_platform('linux',Path(folder),{'XDG_DATA_HOME':folder+'/data','XDG_CONFIG_HOME':folder+'/config'})
   repo=ProfileRepository(platform);repo.create('eden_demo','Eden Demo','approved-eden')
   pin=ApprovedPinAdapter(platform,Path(__file__).resolve().parents[1]/'eden_native'/'approved_models'/'parent_pin.py');pin.set_pin('1234')
   for width,height in ((1920,1080),(1024,768),(800,600)):
    window=create_window(pin_adapter=pin,profiles=repo)
    try:
     window.resize(width,height);window.show();self.app.processEvents()
     next(b for b in window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()=='Eden Demo').click();self.app.processEvents()
     next(b for b in window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()=='My Sticker Garden').click();self.app.processEvents()
     window.resize(width,height);window.render();self.app.processEvents()
     panel=window.controls_widget.findChildren(QWidget,'stickerGardenThreePanel')[-1]
     board=window.controls_widget.findChildren(QWidget,'stickerGardenBoard')[-1]
     self.assertLessEqual(panel.width(),window.scroll_area.viewport().width(),(width,height,panel.width()))
     self.assertFalse(window.scroll_area.horizontalScrollBar().isVisible())
     self.assertGreaterEqual(board.height(),500 if width==1920 else 310)
     self.assertLessEqual(board.width(),810)
     if width==800:self.assertTrue(window.scroll_area.verticalScrollBar().isVisible())
    finally:
     window.close();self.app.processEvents()

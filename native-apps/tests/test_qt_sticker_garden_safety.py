import tempfile, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.sticker_garden import load_garden

class StickerGardenSafetyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  plat=detect_platform('linux',Path(self.tmp.name),{'XDG_DATA_HOME':self.tmp.name+'/data','XDG_CONFIG_HOME':self.tmp.name+'/config'})
  repo=ProfileRepository(plat);repo.create('eden_demo','Eden Demo','approved-eden')
  pin=ApprovedPinAdapter(plat,Path(__file__).resolve().parents[1]/'eden_native'/'approved_models'/'parent_pin.py');pin.set_pin('1234')
  self.window=create_window(pin_adapter=pin,profiles=repo);self.window.show();self.app.processEvents()
  for label in ('Eden Demo','My Sticker Garden'):
   next(b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()==label).click();self.app.processEvents()
 def tearDown(self):self.window.close();self.app.processEvents();self.tmp.cleanup()
 def test_occupied_slot_cannot_be_accidentally_overwritten(self):
  self.assertTrue(self.window.select_garden_sticker('sticker_apple'))
  self.assertTrue(self.window.place_garden_sticker(4))
  self.assertFalse(self.window.place_garden_sticker(4))
  self.assertEqual(load_garden(self.window.sticker_garden_path(),{'sticker_apple'}),{4:'sticker_apple'})
 def test_clear_confirmation_cancels_on_other_interactions(self):
  self.window.select_garden_sticker('sticker_apple');self.window.place_garden_sticker(4)
  self.assertFalse(self.window.clear_sticker_garden())
  self.assertTrue(self.window.garden_clear_confirm)
  self.assertTrue(self.window.select_garden_slot(4))
  self.assertFalse(self.window.garden_clear_confirm)
  self.assertFalse(self.window.clear_sticker_garden())
  self.assertEqual(load_garden(self.window.sticker_garden_path(),{'sticker_apple'}),{4:'sticker_apple'})
  self.assertTrue(self.window.select_garden_category('Nature'))
  self.assertFalse(self.window.garden_clear_confirm)

import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class OnboardingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  plat=detect_platform("linux",Path(self.tmp.name),{"XDG_DATA_HOME":self.tmp.name+"/data","XDG_CONFIG_HOME":self.tmp.name+"/config"})
  self.repo=ProfileRepository(plat);self.pin=ApprovedPinAdapter(plat,SOURCE)
  self.window=create_window(pin_adapter=self.pin,profiles=self.repo);self.window.show();self.app.processEvents()
 def tearDown(self):self.window.close();self.app.processEvents();self.tmp.cleanup()
 def click(self,label):
  matches=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()==label]
  self.assertEqual(len(matches),1,label);matches[0].click();self.app.processEvents()
 def test_first_parent_pin_and_child(self):
  self.click("Parent setup")
  self.assertEqual(self.window.state.page,"parent")
  self.window.pin_input.setText("2468");self.window.pin_confirm.setText("2468")
  self.click("Set first Parent PIN (demo only)")
  self.assertTrue(self.window.state.parent_unlocked)
  self.window.profile_username.setText("first_child")
  self.window.profile_name.setText("First Child")
  self.click("Create child profile")
  self.assertIsNotNone(self.repo.get("first_child"))
  self.click("Back to profiles")
  self.assertEqual(self.window.state.page,"login")
  self.assertFalse(self.window.state.parent_unlocked)
  self.click("First Child")
  self.assertEqual(self.window.state.page,"home")
 def test_mismatch_does_not_set_pin(self):
  self.click("Parent setup")
  self.window.pin_input.setText("2468");self.window.pin_confirm.setText("1234")
  self.click("Set first Parent PIN (demo only)")
  self.assertFalse(self.pin.has_pin())
  self.assertFalse(self.window.state.parent_unlocked)
if __name__=="__main__":unittest.main()

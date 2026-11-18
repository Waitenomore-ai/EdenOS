import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class QtProfileCreationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-create-profile-")
  platform=detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data","XDG_CONFIG_HOME":self.temp.name+"/config"})
  self.repo=ProfileRepository(platform)
  self.repo.create("starter","Starter","approved-eden")
  self.pin=ApprovedPinAdapter(platform,SOURCE)
  self.pin.set_pin("1234")
  self.window=create_window(pin_adapter=self.pin,profiles=self.repo)
  self.window.show();self.app.processEvents()
 def tearDown(self):
  self.window.close();self.app.processEvents();self.temp.cleanup()
 def click(self,label):
  items=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]
  matches=[b for b in items if isinstance(b,QPushButton) and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(matches),1,label)
  matches[0].click();self.app.processEvents()
 def unlock(self):
  self.click("Starter");self.click("Parent Corner")
  self.assertIsNone(self.window.profile_name)
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
 def test_parent_creates_profile(self):
  self.unlock()
  self.window.profile_username.setText("new_child")
  self.window.profile_name.setText("New Child")
  self.window.profile_avatar.setCurrentText("approved-colby")
  self.click("Create child profile")
  self.assertEqual(self.repo.get("new_child").avatar,"approved-colby")
  self.click("Log out");self.click("New Child")
  self.assertEqual(self.window.state.child_id,"new_child")
 def test_invalid_profile_not_created(self):
  self.unlock()
  self.window.profile_username.setText("../bad")
  self.window.profile_name.setText("Bad")
  self.click("Create child profile")
  self.assertEqual(len(self.repo.all()),1)
 def test_logout_removes_create_controls(self):
  self.unlock();self.click("Log out")
  self.assertIsNone(self.window.profile_name)
  self.assertFalse(self.window.state.parent_unlocked)
if __name__=="__main__":unittest.main()

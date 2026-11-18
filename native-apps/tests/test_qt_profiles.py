import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.qt_app import create_window

class QtProfilesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-qt-profiles-")
  self.repo=ProfileRepository(detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data"}))
  self.repo.create("eden_demo","Eden Demo","approved-eden")
  self.repo.create("colby_demo","Colby Demo","approved-colby")
  self.window=create_window(profiles=self.repo)
  self.window.show();self.app.processEvents()
 def tearDown(self):
  self.window.close();self.app.processEvents();self.temp.cleanup()
 def click(self,label):
  buttons=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]
  matches=[b for b in buttons if isinstance(b,QPushButton) and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(matches),1,label)
  matches[0].click();self.app.processEvents()
 def test_switch_profiles_relocks(self):
  self.click("Eden Demo");self.assertEqual(self.window.state.child_id,"eden_demo")
  self.assertFalse(self.window.avatar_image.pixmap().isNull())
  self.click("Parent");self.assertFalse(self.window.state.parent_unlocked)
  self.click("Log out");self.assertEqual(self.window.state.page,"login")
  self.click("Colby Demo");self.assertEqual(self.window.state.child_id,"colby_demo")
  self.assertFalse(self.window.state.parent_unlocked)
 def test_deleted_profile_does_not_open(self):
  self.repo.path.unlink()
  self.click("Eden Demo")
  self.assertEqual(self.window.state.page,"login")
if __name__=="__main__":unittest.main()

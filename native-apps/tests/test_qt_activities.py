import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class QtActivitiesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-qt-activities-")
  platform=detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data","XDG_CONFIG_HOME":self.temp.name+"/config"})
  self.repo=ProfileRepository(platform)
  self.repo.create("eden_demo","Eden Demo","approved-eden")
  self.pin=ApprovedPinAdapter(platform,SOURCE);self.pin.set_pin("1234")
  self.window=create_window(pin_adapter=self.pin,profiles=self.repo)
  self.window.show();self.app.processEvents()
 def tearDown(self):
  self.window.close();self.app.processEvents();self.temp.cleanup()
 def buttons(self):
  return [b.text() or b.accessibleName() for b in [b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]]
 def click(self,label):
  widgets=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]
  found=[w for w in widgets if isinstance(w,QPushButton) and (w.text()==label or w.accessibleName()==label)]
  self.assertEqual(len(found),1,label);found[0].click();self.app.processEvents()
 def unlock(self):
  self.click("Eden Demo");self.click("Parent Corner")
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
 def test_disable_and_reenable_child_activity(self):
  self.click("Eden Demo")
  self.click("Create");self.assertIn("Art Studio",self.buttons())
  self.click("Back to home");self.click("Parent Corner")
  self.assertEqual(len(self.window.activity_checks),0)
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  self.window.activity_checks["art-studio"].setChecked(False)
  self.click("Save activity choices")
  self.click("Back to child home")
  self.click("Create");self.assertNotIn("Art Studio",self.buttons())
  self.click("Back to home");self.click("Parent Corner");self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  self.assertFalse(self.window.activity_checks["art-studio"].isChecked())
  self.window.activity_checks["art-studio"].setChecked(True)
  self.click("Save activity choices");self.click("Back to child home")
  self.click("Create");self.assertIn("Art Studio",self.buttons())
 def test_logout_relocks_activity_controls(self):
  self.unlock();self.click("Log out")
  self.assertEqual(self.window.activity_checks,{})
  self.assertFalse(self.window.state.parent_unlocked)
if __name__=="__main__":unittest.main()

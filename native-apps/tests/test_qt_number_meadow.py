import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform,NavigationState
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.activity_preferences import ActivityPreferences

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class NumberMeadowIntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  plat=detect_platform("linux",Path(self.tmp.name),{"XDG_DATA_HOME":self.tmp.name+"/data","XDG_CONFIG_HOME":self.tmp.name+"/config"})
  self.repo=ProfileRepository(plat);self.repo.create("eden_demo","Eden Demo","approved-eden")
  pin=ApprovedPinAdapter(plat,SOURCE);pin.set_pin("1234")
  self.window=create_window(pin_adapter=pin,profiles=self.repo)
  self.window.resize(800,600);self.window.show();self.app.processEvents()
 def tearDown(self):self.window.close();self.app.processEvents();self.tmp.cleanup()
 def click(self,label):
  found=[b for b in self.window.findChildren(QPushButton) if b.isVisible() and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(found),1,label);found[0].click();self.app.processEvents()
 def test_round_correct_wrong_and_home(self):
  self.click("Eden Demo");self.click("Learn");self.click("Number Meadow")
  self.assertEqual(self.window.state.page,"number-meadow")
  correct=self.window.number_game.round.count
  wrong=next(v for v in self.window.number_game.round.choices if v!=correct)
  self.click(str(wrong))
  self.assertIn("Try again",self.window.info.text())
  self.click(str(correct))
  self.assertIn("Well done",self.window.info.text())
  self.click("Back to home")
  self.assertEqual(self.window.state.page,"home")
 def test_disabled_cannot_launch_via_callback(self):
  self.click("Eden Demo");self.click("Parent")
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  ActivityPreferences(self.window.session,self.repo).save("eden_demo",{"number-meadow":False})
  self.click("Back to child home")
  self.window.open_activity("number-meadow")
  self.assertEqual(self.window.state.page,"home")
 def test_logout_while_playing(self):
  self.click("Eden Demo");self.click("Learn");self.click("Number Meadow");self.click("Log out")
  self.assertEqual(self.window.state.page,"login")
if __name__=="__main__":unittest.main()

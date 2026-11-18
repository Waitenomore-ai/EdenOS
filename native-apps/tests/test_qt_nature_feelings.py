import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.approved_models.nature_explorer_model import NatureExplorer
from eden_native.approved_models.feelings_model import FeelingsSpace
SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class NatureFeelingsTests(unittest.TestCase):
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
  found=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()==label]
  self.assertEqual(len(found),1,label);found[0].click();self.app.processEvents()
 def test_nature_explorer(self):
  self.click("Eden Demo");self.click("Nature Explorer")
  self.assertIsInstance(self.window.nature_game,NatureExplorer)
  self.click("I found it!")
  self.assertEqual(self.window.nature_game.found_count,1)
  self.click("Next")
  self.assertEqual(self.window.nature_game.current_index,1)
  self.click("Previous")
  self.assertEqual(self.window.nature_game.current_index,0)
  self.click("Back to home")
  self.assertEqual(self.window.state.page,"home")
 def test_feelings_checkin(self):
  self.click("Eden Demo");self.click("Feelings")
  self.assertIsInstance(self.window.feelings_game,FeelingsSpace)
  self.click("🙂 Happy")
  self.assertEqual(self.window.feelings_game.mood.key,"happy")
  self.click("○ 🌬️ Take three slow breaths")
  self.assertEqual(self.window.feelings_game.completed_count,1)
  self.click("Back to home")
  self.assertEqual(self.window.state.page,"home")
if __name__=="__main__":unittest.main()

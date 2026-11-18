import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class CompactGridTests(unittest.TestCase):
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
  buttons=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(buttons),1);buttons[0].click();self.app.processEvents()
 def test_imac_home_three_categories_and_activity_routes(self):
  self.click("Eden Demo")
  grid=self.window.activity_grid
  self.assertEqual(grid.count(),3)
  self.assertEqual(grid.rowCount(),1)
  self.assertEqual(grid.columnCount(),3)
  self.assertEqual(self.window.scroll_area.verticalScrollBar().maximum(),0)
  self.click("Create")
  self.assertEqual(self.window.state.page,"create")
  self.assertEqual(sum(b.text()=="Art Studio" for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()),1)
  self.click("Art Studio")
  self.assertEqual(self.window.state.page,"art-studio")
 def test_parent_checkboxes_four_by_two(self):
  self.click("Eden Demo");self.click("Parent")
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  boxes=list(self.window.activity_checks.values())
  self.assertEqual(len(boxes),8)
  layout=boxes[0].parentWidget().layout()
  self.assertEqual(layout.rowCount(),2)
  self.assertEqual(layout.columnCount(),4)
if __name__=="__main__":unittest.main()

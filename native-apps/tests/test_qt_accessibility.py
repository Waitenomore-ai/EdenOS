import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton,QScrollArea
from PySide6.QtCore import Qt
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class QtAccessibilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-qt-a11y-")
  platform=detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data","XDG_CONFIG_HOME":self.temp.name+"/config"})
  self.repo=ProfileRepository(platform);self.repo.create("eden_demo","Eden Demo","approved-eden")
  self.pin=ApprovedPinAdapter(platform,SOURCE);self.pin.set_pin("1234")
  self.window=create_window(pin_adapter=self.pin,profiles=self.repo)
  self.window.resize(800,600);self.window.show();self.app.processEvents()
 def tearDown(self):
  self.window.close();self.app.processEvents();self.temp.cleanup()
 def click(self,label):
  widgets=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]
  buttons=[w for w in widgets if isinstance(w,QPushButton) and w.text()==label]
  self.assertEqual(len(buttons),1);buttons[0].click();self.app.processEvents()
 def test_scrollable_child_and_parent_controls(self):
  self.assertIsInstance(self.window.scroll_area,QScrollArea)
  self.click("Eden Demo")
  self.assertEqual(self.window.scroll_area.verticalScrollBar().maximum(),0)
  self.click("Parent Corner")
  self.assertEqual(self.window.pin_input.accessibleName(),"Parent PIN")
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  self.assertGreaterEqual(self.window.scroll_area.verticalScrollBar().maximum(),0)
  self.assertEqual(self.window.profile_name.accessibleName(),"Child display name")
  self.assertEqual(len(self.window.activity_checks),8)
  for checkbox in self.window.activity_checks.values():
   self.assertTrue(checkbox.accessibleName().startswith("Enable "))
 def test_buttons_keyboard_focus_and_labels(self):
  self.click("Eden Demo")
  for widget in [b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible()]:
   if isinstance(widget,QPushButton):
    self.assertTrue(widget.accessibleName())
    if widget.text(): self.assertEqual(widget.accessibleName(),widget.text())
    self.assertEqual(widget.focusPolicy(),Qt.FocusPolicy.StrongFocus)
if __name__=="__main__":unittest.main()

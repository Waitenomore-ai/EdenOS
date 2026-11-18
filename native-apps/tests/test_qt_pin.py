import os,tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton,QLineEdit
from eden_native.qt_app import create_window
from eden_native.core import detect_platform
from eden_native.approved_pin import ApprovedPinAdapter

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class QtPinTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-qt-pin-")
  self.adapter=ApprovedPinAdapter(detect_platform("linux",Path(self.temp.name),{"XDG_CONFIG_HOME":self.temp.name+"/config"}),SOURCE)
  self.window=create_window(pin_adapter=self.adapter)
  self.window.show();self.app.processEvents()
 def tearDown(self):
  self.window.close();self.app.processEvents();self.temp.cleanup()
 def click(self,label):
  matches=[b for b in self.window.findChildren(QPushButton) if b.isVisible()]
  matches=[b for b in matches if isinstance(b,QPushButton) and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(matches),1,label)
  matches[0].click();self.app.processEvents()
 def input(self,value):
  entry=self.window.pin_input
  self.assertIsNotNone(entry)
  entry.setText(value)
 def parent(self):
  self.click("Preview child session");self.click("Parent")
  self.assertFalse(self.window.state.parent_unlocked)
 def test_setup_unlock_logout_and_relock(self):
  self.parent()
  self.input("1234");self.window.pin_confirm.setText("1234");self.click("Set first Parent PIN (demo only)")
  self.assertTrue(self.window.state.parent_unlocked)
  self.click("Log out");self.assertFalse(self.window.state.parent_unlocked)
  self.click("Preview child session");self.click("Parent")
  self.input("0000");self.click("Unlock Parent Corner")
  self.assertFalse(self.window.state.parent_unlocked)
  self.input("1234");self.click("Unlock Parent Corner")
  self.assertTrue(self.window.state.parent_unlocked)
 def test_invalid_pin_rejected(self):
  self.parent();self.input("12");self.window.pin_confirm.setText("12");self.click("Set first Parent PIN (demo only)")
  self.assertFalse(self.adapter.has_pin())
  self.assertFalse(self.window.state.parent_unlocked)
 def test_mismatched_setup_rejected(self):
  self.parent();self.input("1234");self.window.pin_confirm.setText("5678")
  self.click("Set first Parent PIN (demo only)")
  self.assertFalse(self.adapter.has_pin())
  self.assertFalse(self.window.state.parent_unlocked)
 def test_parent_back_relocks(self):
  self.adapter.set_pin("1234");self.parent()
  self.input("1234");self.click("Unlock Parent Corner")
  self.click("Back to child home")
  self.assertFalse(self.window.state.parent_unlocked)
if __name__=="__main__":unittest.main()

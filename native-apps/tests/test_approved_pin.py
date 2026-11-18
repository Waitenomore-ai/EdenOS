import tempfile,unittest
from pathlib import Path
from eden_native.core import detect_platform,NavigationState
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.parent_session import ParentSession

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class ApprovedPinTests(unittest.TestCase):
 def test_real_approved_model(self):
  with tempfile.TemporaryDirectory(prefix="eden-native-pin-") as root:
   p=detect_platform("linux",Path(root),{"XDG_CONFIG_HOME":str(Path(root)/"config")})
   adapter=ApprovedPinAdapter(p,SOURCE)
   self.assertFalse(adapter.has_pin())
   adapter.set_pin("1234")
   self.assertTrue(adapter.has_pin())
   self.assertTrue(adapter.verify_pin("1234"))
   self.assertFalse(adapter.verify_pin("0000"))
   session=ParentSession(NavigationState().select_child("demo").open_parent(),adapter.verify_pin)
   self.assertFalse(session.authenticate("0000"))
   self.assertTrue(session.authenticate("1234"))
   session.require_parent()
   session.logout()
   with self.assertRaises(PermissionError):session.require_parent()
   self.assertTrue((p.config_root/"parent-pin.json").is_file())
 def test_separate_instances_are_isolated(self):
  with tempfile.TemporaryDirectory(prefix="eden-native-pin-") as root:
   a=ApprovedPinAdapter(detect_platform("win32",Path(root),{"APPDATA":root+"/a","LOCALAPPDATA":root+"/a"}),SOURCE)
   b=ApprovedPinAdapter(detect_platform("darwin",Path(root)/"b",{}),SOURCE)
   a.set_pin("1234")
   self.assertTrue(a.verify_pin("1234"))
   self.assertFalse(b.has_pin())
if __name__=="__main__":unittest.main()

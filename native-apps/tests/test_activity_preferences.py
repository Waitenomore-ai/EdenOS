import tempfile,unittest
from pathlib import Path
from eden_native.core import detect_platform,NavigationState
from eden_native.parent_session import ParentSession
from eden_native.profiles import ProfileRepository
from eden_native.activity_preferences import ActivityPreferences,ACTIVITIES

class ActivityPreferencesTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-activities-")
  self.repo=ProfileRepository(detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data"}))
  self.repo.create("eden_demo","Eden Demo","approved-eden")
  self.session=ParentSession(NavigationState().select_child("eden_demo").open_parent(),lambda pin:pin=="1234")
  self.prefs=ActivityPreferences(self.session,self.repo)
 def tearDown(self):self.temp.cleanup()
 def test_denied_before_auth_and_after_logout(self):
  with self.assertRaises(PermissionError):self.prefs.save("eden_demo",{"art-studio":False})
  self.session.authenticate("1234")
  self.prefs.save("eden_demo",{"art-studio":False})
  self.assertEqual(self.prefs.load("eden_demo"),{"art-studio":False})
  self.session.logout()
  with self.assertRaises(PermissionError):self.prefs.save("eden_demo",{"art-studio":True})
 def test_reject_unknown_child(self):
  self.session.authenticate("1234")
  with self.assertRaises(ValueError):self.prefs.save("missing",{"art-studio":True})
 def test_reject_unknown_activity(self):
  self.session.authenticate("1234")
  with self.assertRaises(ValueError):self.prefs.save("eden_demo",{"not-an-activity":True})
 def test_reject_non_boolean(self):
  self.session.authenticate("1234")
  with self.assertRaises(ValueError):self.prefs.save("eden_demo",{"art-studio":1})
 def test_symlink_not_followed(self):
  self.session.authenticate("1234")
  self.prefs.root.mkdir(parents=True,exist_ok=True)
  target=Path(self.temp.name)/"target"
  target.write_text("protected")
  (self.prefs.root/"eden_demo.json").symlink_to(target)
  with self.assertRaises(ValueError):self.prefs.save("eden_demo",{"art-studio":True})
  self.assertEqual(target.read_text(),"protected")
 def test_eight_known_activities(self):
  self.assertEqual(len(ACTIVITIES),8)
if __name__=="__main__":unittest.main()

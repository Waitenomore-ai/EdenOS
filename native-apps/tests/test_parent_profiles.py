import tempfile,unittest
from pathlib import Path
from eden_native.core import detect_platform,NavigationState
from eden_native.parent_session import ParentSession
from eden_native.parent_profiles import ParentProfileService
from eden_native.profiles import ProfileRepository

class ParentProfileServiceTests(unittest.TestCase):
 def test_requires_unlock_and_relocks_on_logout(self):
  with tempfile.TemporaryDirectory() as d:
   repo=ProfileRepository(detect_platform("linux",Path(d),{"XDG_DATA_HOME":d+"/data"}))
   session=ParentSession(NavigationState().select_child("demo").open_parent(),lambda pin:pin=="1234")
   service=ParentProfileService(session,repo)
   with self.assertRaises(PermissionError):service.create("eden_demo","Eden Demo","approved-eden")
   self.assertEqual(repo.all(),())
   self.assertTrue(session.authenticate("1234"))
   service.create("eden_demo","Eden Demo","approved-eden")
   self.assertEqual(len(repo.all()),1)
   session.logout()
   with self.assertRaises(PermissionError):service.create("colby_demo","Colby Demo","approved-colby")
   self.assertEqual(len(repo.all()),1)
if __name__=="__main__":unittest.main()

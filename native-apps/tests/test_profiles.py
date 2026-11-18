import tempfile,unittest
from pathlib import Path
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository,SELECTABLE_AVATARS
from eden_native.approved_models.profile_cards import make_profile_card

class ProfileTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="eden-native-profile-")
  self.platform=detect_platform("linux",Path(self.temp.name),{"XDG_DATA_HOME":self.temp.name+"/data"})
  self.repo=ProfileRepository(self.platform)
 def tearDown(self):self.temp.cleanup()
 def test_approved_avatar_count(self):
  self.assertEqual(len(SELECTABLE_AVATARS),11)
 def test_create_and_reload(self):
  p=self.repo.create("eden_demo","Eden Demo","approved-eden")
  self.assertEqual(self.repo.get("eden_demo"),p)
  self.assertEqual(len(ProfileRepository(self.platform).all()),1)
 def test_reject_invalid_avatar(self):
  with self.assertRaises(ValueError):self.repo.create("eden_demo","Eden Demo","/tmp/evil.png")
 def test_reject_duplicate(self):
  self.repo.create("eden_demo","Eden Demo","approved-eden")
  with self.assertRaises(ValueError):self.repo.create("eden_demo","Another","approved-colby")
 def test_empty_profiles(self):
  self.assertEqual(self.repo.all(),())
 def test_invalid_name(self):
  with self.assertRaises(ValueError):self.repo.create("../bad","Demo","approved-eden")
if __name__=="__main__":unittest.main()

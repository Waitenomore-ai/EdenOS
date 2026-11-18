import tempfile,unittest
from pathlib import Path
from eden_native.avatars import resolve_avatar,DEFAULT_AVATAR_ROOT
from eden_native.approved_models.profile_cards import SELECTABLE_AVATARS

class AvatarTests(unittest.TestCase):
 def test_all_approved_avatar_pngs_present(self):
  self.assertEqual(len(SELECTABLE_AVATARS),11)
  for name in SELECTABLE_AVATARS:
   self.assertIsNotNone(resolve_avatar(name),name)
 def test_reject_arbitrary_paths(self):
  self.assertIsNone(resolve_avatar("../../etc/passwd"))
  self.assertIsNone(resolve_avatar("approved-unknown"))
 def test_reject_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"approved-eden.png"
   p.symlink_to(DEFAULT_AVATAR_ROOT/"approved-eden.png")
   self.assertIsNone(resolve_avatar("approved-eden",Path(d)))
if __name__=="__main__":unittest.main()

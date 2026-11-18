import unittest
from eden_native.core import NavigationState
from eden_native.parent_session import ParentSession

class ParentSessionTests(unittest.TestCase):
 def test_denies_without_parent_page(self):
  s=ParentSession(NavigationState(),lambda pin:True)
  self.assertFalse(s.authenticate("1234"))
  with self.assertRaises(PermissionError):s.save_parent_setting(lambda:None)
 def test_wrong_pin_does_not_unlock(self):
  s=ParentSession(NavigationState().select_child("demo").open_parent(),lambda pin:pin=="1234")
  self.assertFalse(s.authenticate("0000"))
  self.assertFalse(s.state.parent_unlocked)
 def test_authorised_write(self):
  called=[]
  s=ParentSession(NavigationState().select_child("demo").open_parent(),lambda pin:pin=="1234")
  self.assertTrue(s.authenticate("1234"))
  s.save_parent_setting(lambda:called.append("saved"))
  self.assertEqual(called,["saved"])
 def test_child_change_revokes_access(self):
  s=ParentSession(NavigationState().select_child("demo").open_parent(),lambda pin:True)
  s.authenticate("1234")
  s.change_child("another")
  with self.assertRaises(PermissionError):s.save_parent_setting(lambda:None)
 def test_logout_revokes_access(self):
  s=ParentSession(NavigationState().select_child("demo").open_parent(),lambda pin:True)
  s.authenticate("1234");s.logout()
  with self.assertRaises(PermissionError):s.require_parent()
 def test_invalid_pin_type(self):
  s=ParentSession(NavigationState().open_parent(),lambda pin:True)
  self.assertFalse(s.authenticate(None))
if __name__=="__main__":unittest.main()

import unittest
from pathlib import Path
from eden_native.core import detect_platform, NavigationState

class PlatformTests(unittest.TestCase):
    def test_linux(self):
        p=detect_platform("linux",Path("/home/demo"),{"XDG_CONFIG_HOME":"/tmp/cfg"})
        self.assertEqual(p.config_root,Path("/tmp/cfg/eden-os"))
        self.assertTrue(p.supports_kiosk)
    def test_windows(self):
        p=detect_platform("win32",Path("C:/Users/Demo"),{"APPDATA":"C:/Roaming","LOCALAPPDATA":"C:/Local"})
        self.assertEqual(p.name,"windows")
        self.assertEqual(p.config_root,Path("C:/Roaming/EdenOS"))
        self.assertFalse(p.supports_kiosk)
    def test_macos(self):
        p=detect_platform("darwin",Path("/Users/demo"),{})
        self.assertEqual(p.data_root,Path("/Users/demo/Library/Application Support/EdenOS"))
    def test_unsupported(self):
        with self.assertRaises(RuntimeError):detect_platform("plan9",Path("/tmp"),{})
class NavigationTests(unittest.TestCase):
    def test_login_and_logout(self):
        self.assertEqual(NavigationState().select_child("demo").logout(),NavigationState())
    def test_parent_locked(self):
        s=NavigationState().select_child("demo").open_parent()
        self.assertFalse(s.parent_unlocked)
        self.assertFalse(s.unlock_parent(False).parent_unlocked)
        self.assertTrue(s.unlock_parent(True).parent_unlocked)
        self.assertFalse(s.unlock_parent(True).logout().parent_unlocked)
    def test_change_child_resets_auth(self):
        s=NavigationState().select_child("a").open_parent().unlock_parent(True)
        self.assertFalse(s.select_child("b").parent_unlocked)
    def test_invalid_child_id(self):
        for bad in ("","../x","a/b",None):
            with self.assertRaises(ValueError):NavigationState().select_child(bad)
    def test_cannot_unlock_outside_parent(self):
        self.assertFalse(NavigationState().unlock_parent(True).parent_unlocked)
if __name__=="__main__":unittest.main()

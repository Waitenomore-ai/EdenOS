import os, sys, tempfile, unittest
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from native_eden_v0.window import EdenNativeWindow

class NativeWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["XDG_CONFIG_HOME"] = self.tmp.name
        self.window = EdenNativeWindow()
        self.window.show()
        self.app.processEvents()
    def tearDown(self):
        # Drain Qt's deferred widget deletion before releasing the Python wrapper.
        # Otherwise rapid offscreen test windows can crash during interpreter exit.
        from PySide6.QtCore import QCoreApplication, QEvent
        self.window.close()
        self.window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()
        del self.window
        self.tmp.cleanup()
    def test_eleven_approved_demo_characters(self):
        self.assertEqual(self.window.character_count(), 11)
        self.assertIn("Eden", self.window.character_names())
    def test_approved_portraits_render_on_all_character_buttons(self):
        from PySide6.QtWidgets import QPushButton
        buttons = [b for b in self.window.findChildren(QPushButton) if b.property("avatar_id")]
        self.assertEqual(len(buttons), 11)
        self.assertTrue(all(not b.icon().isNull() for b in buttons))
    def test_existing_profile_chooser(self):
        self.window.choose_character(2)
        self.assertEqual(self.window.selected_profile_id(), "demo_mila")
    def test_profile_selection_opens_child_home_and_logout_returns_to_chooser(self):
        self.assertEqual(self.window.current_page(), "login")
        self.assertEqual(self.window.choose_character(2), "demo_mila")
        self.assertEqual(self.window.current_page(), "home")
        self.assertEqual(self.window.home_actions(), ("Play", "Learn", "Create"))
        self.window.logout()
        self.assertEqual(self.window.current_page(), "login")
        self.assertIsNone(self.window.selected_profile_id())
        self.assertFalse(self.window.parent_is_unlocked())

    def test_child_home_has_approved_imac_artwork_for_three_actions(self):
        from PySide6.QtWidgets import QPushButton
        self.window.choose_character(0)
        buttons = [button for button in self.window._child_home.findChildren(QPushButton)
                   if button.text() in ("Play", "Learn", "Create")]
        self.assertEqual(len(buttons), 3)
        self.assertTrue(all(not button.icon().isNull() for button in buttons))
        self.assertTrue(all(button.iconSize().width() >= 180 for button in buttons))

    def test_child_home_navigation_never_opens_unimplemented_games(self):
        self.window.choose_character(0)
        self.assertFalse(self.window.navigate_home_action("Play"))
        self.assertEqual(self.window.current_page(), "home")

    def test_parent_corner_can_return_to_selected_child_home(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.window.choose_character(0)
        self.window._show_parent()
        self.assertTrue(self.window.unlock_parent("482761"))
        self.window.return_home()
        self.assertEqual(self.window.current_page(), "home")
        self.assertFalse(self.window.parent_is_unlocked())

    def test_parent_locked_without_pin(self):
        self.assertFalse(self.window.parent_is_unlocked())
        self.assertFalse(self.window.unlock_parent("1234"))
    def test_existing_parent_pin(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.assertFalse(self.window.unlock_parent("482762"))
        self.assertTrue(self.window.unlock_parent("482761"))
    def test_unlocked_parent_categories_and_selected_child(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.window.choose_character(2)
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertEqual(self.window.parent_sections(), ("Child Profiles", "Activity Controls", "Learning Progress", "Garden Stars", "PIN & Security"))
        self.assertIn("Mila", self.window.parent_child_summary())
    def test_child_profiles_section_uses_existing_chooser_data(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.window.choose_character(2)
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertTrue(self.window._switch_parent_section("Child Profiles"))
        details = self.window.parent_section_description()
        self.assertIn("11 demonstration profiles", details)
        self.assertIn("Mila", details)
        self.assertIn("Eden", details)

    def test_security_button_displays_ampersand_not_shortcut_underscore(self):
        from PySide6.QtWidgets import QPushButton
        matches = [button for button in self.window.findChildren(QPushButton) if "Security" in button.text()]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].text(), "PIN && Security")

    def test_activity_controls_shows_reviewed_catalogue_not_fake_preferences(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        from native_eden_v0.eden_core.activity_visibility import REVIEWED_RATINGS
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertTrue(self.window._switch_parent_section("Activity Controls"))
        details = self.window.parent_section_description()
        self.assertIn(str(len(REVIEWED_RATINGS)), details)
        self.assertIn("story-garden", details)
        self.assertIn("no child-specific choices loaded", details)

    def test_learning_progress_does_not_claim_real_child_progress(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertTrue(self.window._switch_parent_section("Learning Progress"))
        self.assertIn("no learning records loaded", self.window.parent_section_description())

    def test_garden_stars_uses_approved_catalogue_without_balances(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        from native_eden_v0.eden_core.garden_stars import CATALOGUE, ACTIVITIES
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertTrue(self.window._switch_parent_section("Garden Stars"))
        details = self.window.parent_section_description()
        self.assertIn(f"{len(CATALOGUE)} approved stickers", details)
        self.assertIn(f"{len(ACTIVITIES)} rewardable activities", details)
        self.assertIn("no balances loaded", details)

    def test_security_view_reports_pin_configured_without_exposing_it(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.assertTrue(self.window._switch_parent_section("PIN & Security"))
        details = self.window.parent_section_description()
        self.assertIn("Parent PIN configured", details)
        self.assertNotIn("482761", details)

    def test_locked_parent_cannot_switch_sections(self):
        self.assertFalse(self.window._switch_parent_section("Garden Stars"))
        self.assertFalse(self.window._switch_parent_section("Child Profiles"))

    def test_parent_cannot_reopen_without_new_pin_after_relock(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.window.return_home()
        self.assertFalse(self.window._switch_parent_section("PIN & Security"))
        self.window._show_parent()
        self.assertFalse(self.window.parent_is_unlocked())
        self.assertFalse(self.window.unlock_parent("482762"))
        self.assertTrue(self.window.unlock_parent("482761"))

    def test_parent_corner_buttons_have_accessible_names(self):
        from PySide6.QtWidgets import QPushButton
        buttons = [b for b in self.window.findChildren(QPushButton) if b.text() in ("Parent Corner", "Unlock Parent Corner", "Lock Parent Corner and Return Home")]
        self.assertEqual(len(buttons), 3)
        self.assertTrue(all(b.accessibleName() for b in buttons))

    def test_parent_corner_click_unlock_and_relock_flow(self):
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtTest import QTest
        from PySide6.QtCore import Qt
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        controls = {b.text(): b for b in self.window.findChildren(QPushButton)}
        QTest.mouseClick(controls["Parent Corner"], Qt.MouseButton.LeftButton)
        self.assertFalse(self.window.parent_is_unlocked())
        self.window._pin.setText("482761")
        QTest.mouseClick(controls["Unlock Parent Corner"], Qt.MouseButton.LeftButton)
        self.assertTrue(self.window.parent_is_unlocked())
        QTest.mouseClick(controls["Lock Parent Corner and Return Home"], Qt.MouseButton.LeftButton)
        self.assertFalse(self.window.parent_is_unlocked())

    def test_parent_relocks_on_home(self):
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.assertTrue(self.window.unlock_parent("482761"))
        self.window.return_home()
        self.assertFalse(self.window.parent_is_unlocked())

    def test_enter_key_submits_parent_pin(self):
        from PySide6.QtTest import QTest
        from PySide6.QtCore import Qt
        from native_eden_v0.eden_core.parent_pin import set_pin
        set_pin("482761")
        self.window._show_parent()
        self.window._pin.setFocus()
        self.window._pin.setText("482761")
        QTest.keyClick(self.window._pin, Qt.Key.Key_Return)
        self.assertTrue(self.window.parent_is_unlocked())

    def test_parent_pin_receives_focus_when_opened(self):
        self.window._show_parent()
        self.app.processEvents()
        self.assertTrue(self.window._pin.hasFocus())

    def test_native_window_can_use_existing_child_card_format(self):
        import json
        path = Path(self.tmp.name) / "profiles.json"
        path.write_text(json.dumps({"profiles": [
            {"username": "sample_one", "display_name": "Sample One", "avatar": "approved-eden"},
            {"username": "sample_two", "display_name": "Sample Two", "avatar": "approved-mila"}
        ]}), encoding="utf-8")
        other = EdenNativeWindow(profile_source=path)
        try:
            other.show()
            self.app.processEvents()
            self.assertEqual(other.character_count(), 2)
            self.assertEqual(other.character_names(), ["Sample One", "Sample Two"])
            self.assertEqual(other.choose_character(1), "sample_two")
            self.assertEqual(other.selected_profile_id(), "sample_two")
        finally:
            other.close()
            other.deleteLater()
            self.app.processEvents()

if __name__ == "__main__":
    unittest.main()

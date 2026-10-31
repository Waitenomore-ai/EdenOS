import unittest

from eden_shell.profile_cards import AVATARS
from eden_shell.profile_editor_model import ProfileEditor


class ProfileEditorTests(unittest.TestCase):
    def test_editor_starts_with_default_avatar_and_preview(self):
        editor = ProfileEditor("sam", "Sam")
        self.assertEqual(editor.avatar, AVATARS[0])
        self.assertEqual(editor.preview().public_card, {"display_name": "Sam", "avatar": AVATARS[0]})

    def test_editor_updates_name_and_avatar_only_from_allowed_choices(self):
        editor = ProfileEditor("sam", "Sam")
        editor.set_display_name("  Sammy  ")
        self.assertTrue(editor.choose_avatar("butterfly"))
        self.assertFalse(editor.choose_avatar("/tmp/secret.png"))
        card = editor.preview()
        self.assertEqual(card.public_card, {"display_name": "Sammy", "avatar": "butterfly"})
        self.assertEqual(card.username, "sam")

    def test_reset_returns_to_default_without_changing_account_mapping(self):
        editor = ProfileEditor("sam", "Sam")
        editor.set_display_name("Sammy")
        editor.choose_avatar("tree")
        editor.reset()
        self.assertEqual(editor.preview().public_card, {"display_name": "Sam", "avatar": AVATARS[0]})
        self.assertEqual(editor.preview().username, "sam")


if __name__ == "__main__":
    unittest.main()

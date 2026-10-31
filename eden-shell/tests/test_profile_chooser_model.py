import unittest


class ProfileChooserTests(unittest.TestCase):
    def test_builds_greeter_safe_tiles_and_selects_internal_account(self):
        from eden_shell.profile_cards import make_profile_card
        from eden_shell.profile_chooser_model import ProfileChooser

        chooser = ProfileChooser(
            [
                make_profile_card("sam", "Sam", "butterfly"),
                make_profile_card("lee", "Lee", "tree"),
            ]
        )

        self.assertEqual(
            chooser.tiles(),
            [
                {"display_name": "Sam", "avatar": "butterfly"},
                {"display_name": "Lee", "avatar": "tree"},
            ],
        )
        self.assertEqual(chooser.select(0), "sam")
        self.assertEqual(chooser.selected_public_card(), {"display_name": "Sam", "avatar": "butterfly"})

    def test_invalid_selection_keeps_fallback_and_clears_selection(self):
        from eden_shell.profile_cards import make_profile_card
        from eden_shell.profile_chooser_model import ProfileChooser

        chooser = ProfileChooser([make_profile_card("sam", "Sam", "sun")])
        self.assertIsNone(chooser.select(4))
        self.assertIsNone(chooser.selected_username())
        self.assertIsNone(chooser.selected_public_card())
        self.assertTrue(chooser.text_login_available)


if __name__ == "__main__":
    unittest.main()

import unittest


class ProfileCardTests(unittest.TestCase):
    def test_valid_card_exposes_only_name_and_avatar_to_greeter(self):
        from eden_shell.profile_cards import make_profile_card, public_card

        card = make_profile_card("sam", "Sam", "butterfly")
        self.assertEqual(public_card(card), {"display_name": "Sam", "avatar": "butterfly"})
        self.assertNotIn("username", public_card(card))

    def test_rejects_custom_paths_and_invalid_names(self):
        from eden_shell.profile_cards import make_profile_card

        for avatar in ("/tmp/secret.png", "../other-child", ""):
            with self.subTest(avatar=avatar):
                with self.assertRaises(ValueError):
                    make_profile_card("sam", "Sam", avatar)
        with self.assertRaises(ValueError):
            make_profile_card("sam", "\n", "sun")

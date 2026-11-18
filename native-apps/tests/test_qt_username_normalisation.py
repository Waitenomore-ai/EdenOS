"""Regression: capitalised child usernames must not block onboarding."""
import unittest
from test_qt_profile_creation import QtProfileCreationTests


class UsernameNormalisationTests(QtProfileCreationTests):
    def test_capitalised_name_can_create_profile(self):
        self.unlock()
        self.window.profile_username.setText("Chris")
        self.window.profile_name.setText("Chris")
        self.window.profile_avatar.setCurrentText("approved-colby")
        self.click("Create child profile")
        profile = self.repo.get("chris")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.display_name, "Chris")


if __name__ == "__main__":
    unittest.main()

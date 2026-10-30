import unittest
from eden_shell.setup_model import validate_child_profile
from eden_shell.setup_crypto import hash_password


class PasswordInputTests(unittest.TestCase):
    def test_profile_rejects_control_characters_in_passphrases(self):
        for control in ('\n', '\r', '\x00', '\t', '\x7f'):
            password = 'long-enough' + control + 'suffix'
            with self.subTest(control=repr(control)):
                with self.assertRaises(ValueError):
                    validate_child_profile('Sam', 'sam', password, password)

    def test_hashing_rejects_control_characters_before_openssl(self):
        for control in ('\n', '\r', '\x00', '\t', '\x7f'):
            with self.subTest(control=repr(control)):
                with self.assertRaises(ValueError):
                    hash_password('long-enough' + control + 'suffix')

    def test_unicode_and_spaces_are_valid_passphrase_characters(self):
        password = 'a lovely café garden'
        profile = validate_child_profile('Sam', 'sam', password, password)
        self.assertEqual(profile.username, 'sam')
        self.assertTrue(hash_password(password).startswith('$6$'))

"""Account transaction tests against an in-memory AccountsService boundary.

No real users, passwords, system bus calls or privilege changes are made.
"""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


class Variant:
    def __init__(self, signature, values):
        self.values = values
    def unpack(self):
        return self.values
    def get_child_value(self, index):
        return Variant('', self.values[index])
    def get_variant(self):
        return self
    def get_uint64(self):
        return self.values


class Accounts:
    def __init__(self, fail=None, cleanup_fails=False):
        self.fail = fail
        self.cleanup_fails = cleanup_fails
        self.users = {}
        self.calls = []
    def call_sync(self, destination, path, interface, method, params, *rest):
        self.calls.append(method)
        values = params.unpack()
        if method == self.fail or (method == 'DeleteUser' and self.cleanup_fails):
            raise RuntimeError('simulated account service failure')
        if method == 'CreateUser':
            username, nickname, kind = values
            self.users[42] = {'username':username, 'nickname':nickname, 'kind':kind}
            return Variant('(o)', ('/org/freedesktop/Accounts/User42',))
        if method == 'SetXSession':
            self.users[42]['session'] = values[0]
        elif method == 'SetPassword':
            self.users[42]['password_set'] = values[0].startswith('$6$')
        elif method == 'Get':
            return Variant('(v)', (42,))
        elif method == 'DeleteUser':
            del self.users[values[0]]
        return None


def load_service(accounts):
    gi = ModuleType('gi')
    gi.require_version = lambda *_: None
    repository = ModuleType('gi.repository')
    repository.Gio = SimpleNamespace(bus_get_sync=lambda *_: accounts,
                                     BusType=SimpleNamespace(SYSTEM=0),
                                     DBusCallFlags=SimpleNamespace(NONE=0))
    repository.GLib = SimpleNamespace(Variant=Variant, VariantType=SimpleNamespace(new=lambda value:value))
    path = Path(__file__).resolve().parents[1] / 'eden_shell' / 'setup_service.py'
    spec = importlib.util.spec_from_file_location('eden_shell._transaction_test_service', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'gi':gi, 'gi.repository':repository}):
        spec.loader.exec_module(module)
    return module


class SetupTransactionTests(unittest.TestCase):
    def invoke(self, accounts, username='sam', hash_error=False):
        module = load_service(accounts)
        with patch.object(module.Path, 'is_file', return_value=True), \
             patch('pwd.getpwnam', side_effect=KeyError), \
             patch.object(module, 'hash_password', side_effect=RuntimeError('hash failed') if hash_error else None,
                          return_value='$6$synthetic-test-hash'):
            module.create_child_account('Sam', username, 'a valid passphrase')

    def test_success_creates_standard_user_with_eden_session(self):
        accounts = Accounts()
        self.invoke(accounts)
        self.assertEqual(accounts.users[42]['kind'], 0)
        self.assertEqual(accounts.users[42]['session'], 'eden-child')
        self.assertTrue(accounts.users[42]['password_set'])

    def test_session_or_password_failure_removes_only_new_user(self):
        for failure in ('SetXSession', 'SetPassword'):
            with self.subTest(failure=failure):
                accounts = Accounts(fail=failure)
                with self.assertRaisesRegex(RuntimeError, 'new account was removed'):
                    self.invoke(accounts)
                self.assertEqual(accounts.users, {})

    def test_cleanup_failure_requires_adult_inspection(self):
        accounts = Accounts(fail='SetPassword', cleanup_fails=True)
        with self.assertRaisesRegex(RuntimeError, 'adult must check'):
            self.invoke(accounts)
        self.assertIn(42, accounts.users)

    def test_invalid_username_cannot_create_account(self):
        accounts = Accounts()
        with self.assertRaises(ValueError):
            self.invoke(accounts, username='INVALID NAME')
        self.assertEqual(accounts.users, {})

    def test_hash_failure_occurs_before_creating_account(self):
        accounts = Accounts()
        with self.assertRaises(RuntimeError):
            self.invoke(accounts, hash_error=True)
        self.assertNotIn('CreateUser', accounts.calls)

    def test_existing_username_has_helpful_error_before_account_creation(self):
        accounts = Accounts()
        module = load_service(accounts)
        with patch.object(module.Path, 'is_file', return_value=True), \
             patch('pwd.getpwnam', return_value=SimpleNamespace(pw_name='sam')), \
             patch.object(module, 'hash_password', return_value='$6$synthetic-test-hash'):
            with self.assertRaisesRegex(ValueError, 'already in use'):
                module.create_child_account('Sam', 'sam', 'a valid passphrase')
        self.assertEqual(accounts.users, {})

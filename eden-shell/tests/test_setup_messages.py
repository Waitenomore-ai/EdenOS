"""Test safe account errors reaching the adult wizard without GTK or users."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
from eden_shell.setup_model import ChildProfile, UsernameInUseError


class SetupMessageTests(unittest.TestCase):
    def test_existing_name_error_is_shown_in_wizard(self):
        gi=ModuleType('gi')
        gi.require_version=lambda *_: None
        repository=ModuleType('gi.repository')
        callbacks=[]
        repository.Gtk=SimpleNamespace(ApplicationWindow=object, Application=object)
        repository.Gio=SimpleNamespace()
        repository.GLib=SimpleNamespace(idle_add=lambda callback,*args:callbacks.append((callback,args)))
        service=ModuleType('eden_shell.setup_service')
        def create(*args):
            raise UsernameInUseError('That sign-in username is already in use. Choose another name.')
        service.create_child_account=create
        path=Path(__file__).resolve().parents[1]/'eden_shell/setup.py'
        spec=importlib.util.spec_from_file_location('eden_shell._wizard_message_test',path)
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'gi':gi,'gi.repository':repository,'eden_shell.setup_service':service}):
            spec.loader.exec_module(module)
        window=SimpleNamespace(_finish=lambda *_:None)
        module.SetupWindow._create_profile_worker(window,ChildProfile('Sam','sam'),'synthetic passphrase')
        self.assertEqual(len(callbacks),1)
        _,args=callbacks[0]
        self.assertIs(args[0],False)
        self.assertIn('already in use',args[1])
        self.assertNotIn('synthetic passphrase',args[1])

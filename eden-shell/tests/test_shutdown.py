"""Shutdown error handling with a controlled bus; never powers off a host."""
import importlib.util
from pathlib import Path
import queue
import sys
import threading
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


class ShutdownTests(unittest.TestCase):
    def test_slow_denied_request_does_not_block_ui_and_reports_failure(self):
        entered, release, returned = threading.Event(), threading.Event(), threading.Event()
        callbacks = queue.Queue()
        class Connection:
            def call_sync(self, *args):
                entered.set()
                release.wait(3)
                raise RuntimeError('permission denied')
        gi = ModuleType('gi')
        gi.require_version = lambda *_: None
        repository = ModuleType('gi.repository')
        repository.Gio = SimpleNamespace(BusType=SimpleNamespace(SYSTEM=0),
                                         DBusCallFlags=SimpleNamespace(NONE=0),
                                         bus_get_sync=lambda *_: Connection())
        repository.GLib = SimpleNamespace(Error=RuntimeError, Variant=lambda *args:args,
                                          idle_add=lambda callback,*args: callbacks.put((callback,args)))
        repository.Gtk = SimpleNamespace(ApplicationWindow=object, Application=object)
        path = Path(__file__).resolve().parents[1] / 'eden_shell/app.py'
        spec = importlib.util.spec_from_file_location('eden_shell._shutdown_test', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'gi':gi, 'gi.repository':repository}):
            spec.loader.exec_module(module)
        messages=[]
        class Window:
            _request_power_off = module.EdenWindow._request_power_off
            _show_status = lambda self,message: messages.append(message)
        # Bind new helper methods if present, while still exercising old code RED.
        for name in ('_power_off_worker', '_finish_power_off'):
            if hasattr(module.EdenWindow, name):
                setattr(Window, name, getattr(module.EdenWindow, name))
        dialog = SimpleNamespace(close=lambda:None, set_sensitive=lambda value:None)
        window = Window()
        def request():
            try:
                window._request_power_off(dialog)
            finally:
                returned.set()
        caller = threading.Thread(target=request)
        caller.start()
        try:
            self.assertTrue(entered.wait(1), 'Controlled bus was not reached')
            self.assertTrue(returned.wait(0.2), 'Shutdown blocked the UI caller')
        finally:
            release.set()
            caller.join(3)
        callback, args = callbacks.get(timeout=2)
        callback(*args)
        self.assertTrue(messages)
        self.assertIn('adult', messages[-1])
        self.assertFalse(window._shutdown_pending)

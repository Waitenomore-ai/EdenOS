import importlib
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ReleaseGateTests(unittest.TestCase):
    def test_browser_needs_enabled_reviewed_config_and_valid_policy(self):
        browser = importlib.import_module('eden_shell.browser')
        gate = getattr(browser, 'browser_access_ready', None)
        self.assertTrue(callable(gate), 'Browser needs a shared adult-configuration gate')
        policy = ROOT / 'config/includes.chroot/etc/firefox/policies/policies.json'
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'defaults.json'
            for document in ({}, {'browser_enabled': True},
                             {'browser_enabled': True, 'browser_policy': 'kidstube_allowlist_unverified'},
                             {'browser_enabled': False, 'browser_policy': 'kidstube_allowlist_verified'},
                             {'browser_enabled': 'true', 'browser_policy': 'kidstube_allowlist_verified'}):
                config.write_text(json.dumps(document))
                self.assertFalse(gate(config, policy))
            config.write_text(json.dumps({'browser_enabled': True,
                                         'browser_policy': 'kidstube_allowlist_verified'}))
            self.assertTrue(gate(config, policy))
            self.assertFalse(gate(config, Path(directory) / 'missing-policy'))
            config.write_text('{broken')
            self.assertFalse(gate(config, policy))
            config.unlink()
            self.assertFalse(gate(config, policy))

    def test_image_browser_default_is_disabled_until_reviewed(self):
        defaults = json.loads((ROOT / 'config/includes.chroot/etc/eden-os/defaults.json').read_text())
        self.assertIs(defaults['browser_enabled'], False)

    def test_build_label_handles_missing_invalid_and_valid_metadata(self):
        try:
            module = importlib.import_module('eden_shell.version')
        except ModuleNotFoundError:
            self.fail('Build metadata reader is missing')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'build.json'
            self.assertEqual(module.build_label(path), 'Development build — version unavailable')
            path.write_text('[]')
            self.assertEqual(module.build_label(path), 'Development build — version unavailable')
            path.write_text(json.dumps({'version': '0.1-dev', 'commit': 'a'*40,
                                        'built_at': '2026-10-30T20:00:00Z'}))
            label = module.build_label(path)
            self.assertIn('0.1-dev', label)
            self.assertIn('aaaaaaaaaaaa', label)
            self.assertIn('2026-10-30T20:00:00Z', label)

    def test_build_metadata_writer_records_commit_without_personal_details(self):
        import os
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'etc' / 'build.json'
            writer = ROOT / 'scripts/write-build-info'
            self.assertTrue(writer.is_file(), 'Build metadata writer is missing')
            result = subprocess.run(['python3', str(writer), str(destination)],
                                    env=dict(os.environ, EDEN_SOURCE_COMMIT='b'*40),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(destination.read_text())
            self.assertEqual(metadata['commit'], 'b'*40)
            self.assertEqual(metadata['version'], '0.1-dev')
            self.assertEqual(set(metadata), {'commit', 'version', 'built_at'})

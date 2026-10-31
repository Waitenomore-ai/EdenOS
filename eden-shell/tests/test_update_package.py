"""Exercise the real Debian package artifact without installing it."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('dpkg-deb'), 'Needs Debian package tools')
class UpdatePackageTests(unittest.TestCase):
    def test_update_contains_current_launcher_and_preserves_system_preferences(self):
        builder = ROOT / 'scripts/build-update-package'
        self.assertTrue(builder.is_file(), 'An installed iMac needs a Debian update artifact')
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            result = subprocess.run(['python3', str(builder), '--output', str(base),
                                     '--version', '0.1.0~dev6+g123456789abc'],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            deb, = base.glob('*.deb')
            control = subprocess.check_output(['dpkg-deb', '-f', str(deb)], text=True)
            self.assertIn('Package: eden-os-desktop', control)
            self.assertIn('Architecture: all', control)
            self.assertIn('firmware-amd-graphics', control)
            self.assertIn('lightdm-gtk-greeter', control)
            extracted = base / 'unpacked'
            subprocess.run(['dpkg-deb', '-R', str(deb), str(extracted)], check=True)
            self.assertEqual((extracted / 'usr/share/eden-os/eden_shell/app.py').read_bytes(),
                             (ROOT / 'eden-shell/eden_shell/app.py').read_bytes())
            self.assertTrue(os.access(extracted / 'usr/local/bin/eden-shell', os.X_OK))
            for game in ('number-meadow', 'word-woodland', 'story-garden',
                         'art-studio', 'puzzle-pond', 'time-routines',
                         'nature-explorer', 'feelings'):
                wrapper = extracted / 'usr/local/bin' / f'eden-{game}'
                self.assertTrue(os.access(wrapper, os.X_OK), game)
                self.assertIn('export PYTHONPATH=', wrapper.read_text(), game)
                self.assertTrue((extracted / 'usr/share/applications' /
                                 f'eden-{game}.desktop').is_file(), game)
            for picture in ('number-meadow', 'word-woodland', 'story-garden',
                            'art-studio', 'puzzle-pond', 'time-routines',
                            'nature-explorer', 'feelings-quiet-space'):
                asset = extracted / 'usr/share/eden-os/eden_shell/data/activity-art' / f'{picture}.svg'
                self.assertTrue(asset.is_file(), picture)
                self.assertIn('<svg', asset.read_text(), picture)
            home_icons = ('learn', 'play', 'create', 'read', 'numbers', 'words',
                          'puzzles', 'studio', 'explore', 'stuff', 'settings', 'help')
            icon_dir = extracted / 'usr/share/eden-os/eden_shell/data/home-icons'
            for key in home_icons:
                icon = icon_dir / f'{key}.svg'
                self.assertTrue(icon.is_file(), key)
                self.assertIn('<svg', icon.read_text(), key)
            self.assertEqual(len(set((icon_dir / f'{key}.svg').read_bytes()
                                     for key in home_icons)), 12,
                             'Every desktop shortcut needs original artwork')
            self.assertTrue((extracted / 'usr/share/applications/eden-shell.desktop').is_file())
            self.assertTrue((extracted / 'usr/share/eden-os/eden_shell/profile_chooser_model.py').is_file())
            self.assertTrue((extracted / 'usr/share/sounds/edenos/startup.wav').is_file())
            self.assertTrue((extracted / 'usr/local/bin/eden-backup').is_file())
            self.assertIn('/etc/eden-os/defaults.json',
                          (extracted / 'DEBIAN/conffiles').read_text().splitlines())
            self.assertFalse((extracted / 'home').exists(), 'Update must not overwrite child files')
            self.assertFalse((extracted / 'etc/passwd').exists())
            self.assertFalse((extracted / 'etc/fstab').exists())
            self.assertFalse(list(extracted.rglob('*.pyc')))
            manifest = json.loads((extracted / 'usr/share/eden-os/update.json').read_text())
            self.assertEqual(manifest['package_version'], '0.1.0~dev6+g123456789abc')

    def test_invalid_version_fails_before_creating_package(self):
        builder = ROOT / 'scripts/build-update-package'
        self.assertTrue(builder.is_file())
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(['python3', str(builder), '--output', directory,
                                     '--version', 'bad/version'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(directory).glob('*.deb')), [])

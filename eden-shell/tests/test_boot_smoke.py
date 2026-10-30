"""Exercise the boot diagnostic with a controlled emulator executable."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'boot-smoke'


class BootSmokeTests(unittest.TestCase):
    def run_diagnostic(self, status=0, message='', iso_exists=True, mode='bios', firmware=True):
        with tempfile.TemporaryDirectory(prefix='eden boot ') as directory:
            root = Path(directory)
            emulator = root / 'qemu-system-x86_64'
            emulator.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$EDEN_TEST_MESSAGE" "$@"\nexit "$EDEN_TEST_STATUS"\n'
            )
            emulator.chmod(0o755)
            iso = root / 'test image.iso'
            if iso_exists:
                iso.write_bytes(b'disposable test fixture')
            log = root / 'logs' / 'boot.log'
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'],
                       EDEN_TEST_STATUS=str(status), EDEN_TEST_MESSAGE=message)
            code, variables = root / 'CODE.fd', root / 'VARS.fd'
            if firmware:
                code.write_bytes(b'firmware fixture')
                variables.write_bytes(b'unchanged variable fixture')
            env.update(EDEN_OVMF_CODE=str(code), EDEN_OVMF_VARS=str(variables))
            result = subprocess.run(['bash', str(SCRIPT), str(iso), str(log), mode],
                                    env=env, capture_output=True, text=True, timeout=5)
            if firmware:
                self.assertEqual(variables.read_bytes(), b'unchanged variable fixture')
            return result, log.read_text() if log.exists() else ''

    def test_emulator_startup_failure_fails_diagnostic_and_preserves_log(self):
        result, log = self.run_diagnostic(1, 'Could not initialize display')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Could not initialize display', log)
        self.assertIn('QEMU exit status: 1', log)

    def test_unexpected_emulator_exit_fails_diagnostic(self):
        for status in (42, 126, 127, 137):
            with self.subTest(status=status):
                result, _ = self.run_diagnostic(status)
                self.assertNotEqual(result.returncode, 0)

    def test_timeout_is_explicitly_inconclusive(self):
        result, log = self.run_diagnostic(124)
        self.assertEqual(result.returncode, 0)
        self.assertIn('inconclusive', result.stdout.lower())
        self.assertIn('QEMU exit status: 124', log)

    def test_normal_exit_does_not_claim_verified_boot(self):
        result, _ = self.run_diagnostic()
        self.assertEqual(result.returncode, 0)
        self.assertIn('not verified', result.stdout.lower())

    def test_explicit_guest_boot_error_fails_even_when_emulator_exits_normally(self):
        for error in ('Kernel panic', 'VFS: Unable to mount root',
                      'No bootable device', 'Boot failed'):
            with self.subTest(error=error):
                result, log = self.run_diagnostic(0, error)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(error, log)

    def test_missing_image_fails_before_launch(self):
        result, log = self.run_diagnostic(iso_exists=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ISO not found', result.stderr)
        self.assertEqual(log, '')

    def test_uefi_uses_read_only_code_and_disposable_variables(self):
        result, log = self.run_diagnostic(mode='uefi')
        self.assertEqual(result.returncode, 0)
        self.assertIn('if=pflash,format=raw,readonly=on', log)
        self.assertIn('eden-uefi-', log)

    def test_uefi_rejects_missing_firmware(self):
        result, _ = self.run_diagnostic(mode='uefi', firmware=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('firmware', result.stderr.lower())

    def test_unknown_firmware_mode_is_rejected(self):
        result, _ = self.run_diagnostic(mode='unknown')
        self.assertNotEqual(result.returncode, 0)

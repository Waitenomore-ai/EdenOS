import importlib
import unittest


class IsoBootChecks(unittest.TestCase):
    def checker(self):
        try:
            return importlib.import_module('eden_shell.iso_checks').has_dual_firmware_boot
        except ModuleNotFoundError:
            self.fail('Strict ISO boot-catalog checker is missing')

    def test_requires_bootable_bios_and_uefi_images(self):
        check = self.checker()
        bios = 'El Torito boot img :   1  BIOS  y   none  0x0000 0x00 4 3197\n'
        uefi = 'El Torito boot img :   2  UEFI  y   none  0x0000 0x00 6656 1533\n'
        self.assertTrue(check(bios + uefi))
        for report in ('El Torito images: none', bios, uefi,
                       bios + uefi.replace('UEFI  y', 'UEFI  n'),
                       'Info: BIOS and UEFI boot images were mentioned'):
            with self.subTest(report=report):
                self.assertFalse(check(report))

    def test_efi_header_requires_amd64_application(self):
        import struct
        try:
            check = importlib.import_module('eden_shell.iso_checks').is_amd64_efi_application
        except ModuleNotFoundError:
            self.fail('EFI application header checker is missing')
        binary = bytearray(512)
        binary[:2] = b'MZ'
        struct.pack_into('<I', binary, 0x3c, 0x80)
        binary[0x80:0x84] = b'PE\x00\x00'
        struct.pack_into('<H', binary, 0x84, 0x8664)
        struct.pack_into('<H', binary, 0x94, 240)
        struct.pack_into('<H', binary, 0x98, 0x20b)
        struct.pack_into('<H', binary, 0xdc, 10)
        self.assertTrue(check(bytes(binary)))
        for invalid in (b'', b'not an EFI file', bytes(binary[:200])):
            self.assertFalse(check(invalid))
        binary[0x84:0x86] = b'\x4c\x01'
        self.assertFalse(check(bytes(binary)))
        binary[0x84:0x86] = b'\x64\x86'
        struct.pack_into('<H', binary, 0xdc, 3)
        self.assertFalse(check(bytes(binary)))

    def test_command_fails_when_boot_files_are_missing(self):
        from pathlib import Path
        import os
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, '-m', 'eden_shell.iso_checks',
                                 '/no/such/eden-catalog', '/no/such/eden-loader'],
                                env=dict(os.environ, PYTHONPATH=str(root)),
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Cannot inspect boot files', result.stderr)

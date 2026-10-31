import importlib
import json
from pathlib import Path
import tempfile
import unittest


class DiagnosticsTests(unittest.TestCase):
    def module(self):
        try:
            return importlib.import_module('eden_shell.diagnostics')
        except ModuleNotFoundError:
            self.fail('Read-only diagnostics module is missing')

    def test_reports_hardware_firmware_memory_and_storage_without_serials(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, text in {
                'sys/class/dmi/id/product_name': 'iMac12,2\n',
                'sys/firmware/efi/fw_platform_size': '64\n',
                'proc/meminfo': 'MemTotal:        4194304 kB\n',
                'proc/cpuinfo': 'model name\t: Intel Test CPU\n',
                'proc/cmdline': 'BOOT_IMAGE=/vmlinuz root=UUID=secret ro nomodeset radeon.modeset=0\n',
                'etc/eden-os/build.json': json.dumps({'version':'0.1-dev','commit':'a'*40,'built_at':'today'}),
            }.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            report = module.collect_report(root)
            self.assertEqual(report['hardware_model'], 'iMac12,2')
            self.assertEqual(report['firmware_bits'], '64')
            self.assertEqual(report['memory_bytes'], 4294967296)
            self.assertIn('free_bytes', report['storage'])
            self.assertNotIn('serial', json.dumps(report).lower())
            self.assertNotIn('hostname', report)
            self.assertNotIn('username', report)
            self.assertEqual(report['graphics_boot_flags'], ['nomodeset', 'radeon.modeset=0'])

    def test_storage_budget_uses_binary_thresholds(self):
        assess = self.module().assess_storage
        self.assertTrue(assess(30*2**30, 10*2**30)['within_budget'])
        self.assertFalse(assess(30*2**30, 5*2**30)['within_budget'])
        self.assertFalse(assess(40*2**30, 10*2**30)['within_budget'])

    def test_missing_hardware_data_is_unknown(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            report = module.collect_report(Path(directory))
            self.assertEqual(report['hardware_model'], 'unknown')
            self.assertEqual(report['firmware_bits'], 'unknown')
            self.assertIsNone(report['memory_bytes'])


    def test_live_session_is_detected_from_live_boot_mount(self):
        module = self.module()
        detect = getattr(module, 'is_live_session', None)
        self.assertTrue(callable(detect), 'Live-session detection is missing')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse(detect(root))
            (root / 'run/live/medium').mkdir(parents=True)
            self.assertTrue(detect(root))

    def test_reports_drm_driver_and_pci_identity_without_serials(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / 'sys/class/drm/card0'
            device = card / 'device'
            device.mkdir(parents=True)
            (device / 'vendor').write_text('0x1002\n')
            (device / 'device').write_text('0x6738\n')
            (device / 'uevent').write_text('PCI_SLOT_NAME=0000:01:00.0\n')
            (card / 'status').write_text('connected\n')
            driver = root / 'sys/bus/pci/drivers/radeon'
            driver.mkdir(parents=True)
            (device / 'driver').symlink_to(driver)
            report = module.collect_report(root)
            self.assertEqual(report['graphics'], [{
                'card': 'card0', 'driver': 'radeon', 'status': 'connected', 'vendor': '0x1002',
                'device': '0x6738', 'pci_slot': '0000:01:00.0',
            }])
            self.assertNotIn('serial', json.dumps(report).lower())

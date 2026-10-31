import unittest
from pathlib import Path


class BootSplashTests(unittest.TestCase):
    def test_plymouth_theme_and_quiet_boot_defaults_are_included(self):
        root = Path(__file__).parents[2]
        packages = (root / "config/package-lists/eden.list.chroot_install").read_text(encoding="utf-8")
        theme = root / "config/includes.chroot/usr/share/plymouth/themes/edenos/edenos.plymouth"
        script = root / "config/includes.chroot/usr/share/plymouth/themes/edenos/edenos.script"
        defaults = root / "config/includes.chroot/etc/plymouth/plymouthd.conf"
        grub = root / "config/includes.chroot/etc/default/grub.d/edenos.cfg"
        self.assertIn("plymouth", packages)
        self.assertTrue(theme.is_file())
        self.assertTrue(script.is_file())
        self.assertIn("Name=EdenOS", theme.read_text(encoding="utf-8"))
        self.assertIn("Theme=edenos", defaults.read_text(encoding="utf-8"))
        grub_text = grub.read_text(encoding="utf-8")
        self.assertIn("quiet", grub_text)
        self.assertIn("splash", grub_text)
        self.assertIn("GRUB_CMDLINE_LINUX_RECOVERY", grub_text)
        self.assertIn("nomodeset", grub_text)


if __name__ == "__main__":
    unittest.main()

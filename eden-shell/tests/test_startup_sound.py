import unittest
from pathlib import Path


class StartupSoundTests(unittest.TestCase):
    def test_eden_startup_sound_is_packaged_and_recovery_safe(self):
        root = Path(__file__).parents[2]
        packages = (root / "config/package-lists/eden.list.chroot_install").read_text(encoding="utf-8")
        sound = root / "config/includes.chroot/usr/share/sounds/edenos/startup.wav"
        launcher = root / "config/includes.chroot/usr/local/bin/eden-startup-sound"
        lightdm = root / "config/includes.chroot/etc/lightdm/lightdm.conf.d/50-eden-sound.conf"
        self.assertIn("alsa-utils", packages)
        self.assertTrue(sound.is_file())
        self.assertGreater(sound.stat().st_size, 1000)
        self.assertIn("edenos/startup.wav", launcher.read_text(encoding="utf-8"))
        self.assertIn("nomodeset", launcher.read_text(encoding="utf-8"))
        self.assertIn("greeter-setup-script=/usr/local/bin/eden-startup-sound", lightdm.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

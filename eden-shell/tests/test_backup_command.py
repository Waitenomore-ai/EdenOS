from pathlib import Path
import unittest


class BackupCommandTests(unittest.TestCase):
    def test_backup_command_requires_existing_destination_and_avoids_overwrite(self):
        root = Path(__file__).parents[2]
        command = (root / "config/includes.chroot/usr/local/bin/eden-backup").read_text()
        self.assertIn('Backup destination must be an existing writable directory.', command)
        self.assertIn('mv --no-clobber', command)
        self.assertIn("--exclude='.cache'", command)
        self.assertIn('eden-backup-$USER-$timestamp.tar.gz', command)
        self.assertIn('tar --test --file="$temporary"', command)

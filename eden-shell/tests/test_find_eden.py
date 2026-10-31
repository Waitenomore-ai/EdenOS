"""Verify shipping real Find Eden assets, not just source references."""
import datetime
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class FindEdenIntegrationTests(unittest.TestCase):
    def test_iso_stager_contains_all_manifest_images_and_game(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'find-eden'
            result = subprocess.run(['python3', str(ROOT/'scripts/stage-find-eden'), str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = json.loads((target/'wallpapers.json').read_text())
            self.assertEqual(len(rows), 28)
            for row in rows:
                self.assertEqual((target/row['file']).read_bytes(), (ROOT/'find-eden'/row['file']).read_bytes())
            self.assertEqual((target/'Find-Eden.html').read_bytes(), (ROOT/'find-eden/Find-Eden.html').read_bytes())
            self.assertTrue((target/'daily-wallpaper/rotator.py').is_file())
            self.assertFalse(list(target.rglob('test_*.py')))

    def test_daily_home_image_matches_manifest_date_and_cycle(self):
        from eden_shell.find_eden_assets import today_image
        pack=ROOT/'find-eden'
        self.assertEqual(today_image(pack, datetime.date(2026,10,31)), pack/'wallpapers/find-eden-sunrise.png')
        self.assertEqual(today_image(pack, datetime.date(2026,11,1)), pack/'wallpapers/find-eden-lily-pond.png')
        self.assertEqual(today_image(pack, datetime.date(2026,11,28)), pack/'wallpapers/find-eden-sunrise.png')

    def test_stager_rejects_changed_asset_without_leaving_partial_output(self):
        from eden_shell.find_eden_assets import stage_pack
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source';source.mkdir();(source/'wallpapers.json').write_text(json.dumps([{'id':'x','title':'x','file':'bad.png','sha256':'0'*64}]*28))
            (source/'bad.png').write_bytes(b'not a PNG')
            target=Path(directory)/'target'
            with self.assertRaises(ValueError):stage_pack(source,target)
            self.assertFalse(target.exists())

    def test_native_game_navigation_rejects_other_files_and_websites(self):
        from eden_shell.find_eden import navigation_allowed
        page='file:///usr/share/eden-os/find-eden/Find-Eden.html'
        self.assertTrue(navigation_allowed(page+'#main', page))
        for uri in ['https://example.com','file:///etc/passwd',page+'?other=1']:
            self.assertFalse(navigation_allowed(uri,page))

if __name__=='__main__':unittest.main()

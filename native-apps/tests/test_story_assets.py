import json, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import Qt
from eden_native.qt_app import create_window

ROOT = Path(__file__).resolve().parents[1]
STORY_ROOT = ROOT / "assets" / "stories"

class StoryAssetTests(unittest.TestCase):
    def test_staging_catalogue_is_labelled_and_audio_complete(self):
        data = json.loads((STORY_ROOT / "75-books-staging.json").read_text())
        books = data["books"]
        self.assertEqual(len(books), 75)
        self.assertEqual(sum(len(book["pages"]) for book in books), 762)
        self.assertEqual(sum(book["status"] == "text-draft" for book in books), 63)
        self.assertEqual(sum(book["status"] == "original" for book in books), 12)
        for book in books:
            for index, page in enumerate(book["pages"], 1):
                self.assertTrue(page["text"].strip())
                self.assertTrue((STORY_ROOT / "audio" / book["id"] / f"page-{index:02}.mp3").is_file())

    def test_all_approved_avatar_files_exist(self):
        manifest = ROOT / "assets" / "avatars" / "SHA256SUMS"
        import hashlib
        for line in manifest.read_text().splitlines():
            digest, filename = line.split(maxsplit=1)
            image = ROOT / filename.lstrip("*")
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), digest)

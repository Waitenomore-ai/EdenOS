"""All staged Story Garden pages must have their approved audio file."""
import json
import unittest
from pathlib import Path


class StoryAudioCoverageTests(unittest.TestCase):
    def test_all_75_books_have_every_page_recording(self):
        story_root = Path(__file__).resolve().parents[1] / 'assets' / 'stories'
        books = json.loads((story_root / '75-books-staging.json').read_text(encoding='utf-8'))['books']
        self.assertEqual(len(books), 75)
        total = 0
        for book in books:
            for page_no, _page in enumerate(book['pages'], 1):
                total += 1
                recording = story_root / 'audio' / book['id'] / ('page-%02d.mp3' % page_no)
                self.assertTrue(recording.is_file(), f'Missing {book["title"]} page {page_no}')
                self.assertGreater(recording.stat().st_size, 1024, f'Empty {recording}')
        self.assertEqual(total, 762)

if __name__ == '__main__':
    unittest.main()

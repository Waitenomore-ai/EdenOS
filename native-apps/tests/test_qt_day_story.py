import tempfile, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.approved_models.story_garden_model import SCENES

SOURCE = Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'

class DayStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        plat = detect_platform("linux", Path(self.tmp.name), {"XDG_DATA_HOME": self.tmp.name+"/data", "XDG_CONFIG_HOME": self.tmp.name+"/config"})
        repo = ProfileRepository(plat)
        repo.create("eden_demo", "Eden Demo", "approved-eden")
        pin = ApprovedPinAdapter(plat, SOURCE)
        pin.set_pin("1234")
        self.window = create_window(pin_adapter=pin, profiles=repo)
        self.window.resize(800, 600)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()
        self.tmp.cleanup()

    def click(self, label):
        matches = [b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and (b.text() == label or b.accessibleName() == label)]
        self.assertEqual(len(matches), 1, label)
        matches[0].click()
        self.app.processEvents()

    def test_my_day(self):
        self.click("Eden Demo")
        self.click("Learn"); self.click("My Day")
        self.click("○ 🌞 Wake up")
        self.assertTrue(self.window.day_game.completed[0])
        self.click("Start again")
        self.assertFalse(self.window.day_game.completed[0])

    def test_story_pages(self):
        self.click("Eden Demo")
        self.click("Play"); self.click("Story Garden")
        self.assertEqual(len(self.window.story_books), 75)
        self.click("The Tiny Seed")
        for _ in range(len(SCENES)-1):
            self.click("Next page")
        self.assertEqual(self.window.story_page, len(SCENES)-1)
        self.click("Read again")
        self.assertEqual(self.window.story_page, 0)
        self.click("Choose another book")
        self.click("The Lost Duckling")
        self.assertEqual(self.window.story_books[self.window.story_selected]["title"], "The Lost Duckling")

import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton,QLabel
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.activity_preferences import ActivityPreferences
from eden_native.approved_models.word_woodland_model import WordWoodland
from eden_native.approved_models.puzzle_pond_model import PuzzlePond

SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class GamesIntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  plat=detect_platform("linux",Path(self.tmp.name),{"XDG_DATA_HOME":self.tmp.name+"/data","XDG_CONFIG_HOME":self.tmp.name+"/config"})
  self.repo=ProfileRepository(plat);self.repo.create("eden_demo","Eden Demo","approved-eden")
  pin=ApprovedPinAdapter(plat,SOURCE);pin.set_pin("1234")
  self.window=create_window(pin_adapter=pin,profiles=self.repo)
  self.window.resize(800,600);self.window.show();self.app.processEvents()
 def tearDown(self):self.window.close();self.app.processEvents();self.tmp.cleanup()
 def click(self,label):
  found=[b for b in self.window.findChildren(QPushButton) if b.isVisible() and (b.text()==label or b.accessibleName()==label)]
  self.assertEqual(len(found),1,label);found[0].click();self.app.processEvents()
 def test_word_woodland_correct_and_wrong(self):
  self.click("Eden Demo");self.click("Learn");self.click("Word Woodland")
  self.assertIsInstance(self.window.word_game,WordWoodland)
  rnd=self.window.word_game.round
  self.click(next(x for x in rnd.choices if x!=rnd.answer))
  self.assertIn("Try another",self.window.info.text())
  self.click(rnd.answer)
  self.assertIn("Well done",self.window.info.text())
  self.click("Back to home")
  self.assertEqual(self.window.state.page,"home")
 def test_puzzle_matching_and_mismatch(self):
  self.click("Eden Demo");self.click("Play");self.click("Puzzle Pond")
  self.assertIsInstance(self.window.puzzle_game,PuzzlePond)
  cards=self.window.puzzle_game.cards
  first=cards[0];match=next(c for c in cards[1:] if c.symbol==first.symbol)
  self.window.choose_puzzle(first.index);self.window.choose_puzzle(match.index)
  self.assertTrue(self.window.puzzle_game.cards[first.index].matched)
  remaining=[c for c in self.window.puzzle_game.cards if not c.matched]
  a=remaining[0];b=next(c for c in remaining[1:] if c.symbol!=a.symbol)
  self.window.choose_puzzle(a.index);self.window.choose_puzzle(b.index)
  self.assertIsNotNone(self.window.puzzle_game.second)
  self.window.finish_puzzle_mismatch(self.window.puzzle_game,"eden_demo")
  self.assertIsNone(self.window.puzzle_game.second)
 def test_disabled_word_cannot_open(self):
  self.click("Eden Demo");self.click("Parent")
  self.window.pin_input.setText("1234");self.click("Unlock Parent Corner")
  ActivityPreferences(self.window.session,self.repo).save("eden_demo",{"word-woodland":False})
  self.click("Back to child home")
  self.window.open_activity("word-woodland")
  self.assertEqual(self.window.state.page,"home")
if __name__=="__main__":unittest.main()

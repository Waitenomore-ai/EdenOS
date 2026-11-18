import tempfile, unittest
from pathlib import Path
from eden_native.garden_stars import GardenStars

class GardenStarsTests(unittest.TestCase):
    def test_child_specific_unlock_and_no_free_reward_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine=GardenStars(Path(tmp)/'stars.sqlite3')
            engine.create_profile('child_one')
            engine.create_profile('child_two')
            self.assertEqual(engine.collection('child_one'),[])
            self.assertEqual(engine.collection('child_two'),[])
            with self.assertRaises(ValueError):
                engine.unlock('child_one','sticker_owl')
            self.assertEqual(engine.collection('child_one'),[])
            engine.unlock('child_one','sticker_owl',parent_authorized=True)
            self.assertEqual([item['sku'] for item in engine.collection('child_one')],['sticker_owl'])
            self.assertEqual(engine.collection('child_two'),[])
            self.assertEqual(engine.balance('child_one'),0)

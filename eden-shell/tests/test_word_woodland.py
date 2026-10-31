import random
import unittest


class WordWoodlandTests(unittest.TestCase):
    def test_round_has_answer_and_four_choices(self):
        from eden_shell.word_woodland_model import WordWoodland

        game = WordWoodland(random.Random(3))
        round_ = game.new_round()
        self.assertEqual(len(round_.choices), 4)
        self.assertIn(round_.answer, round_.choices)
        self.assertEqual(round_.word[0], round_.answer)

    def test_answers_do_not_store_progress(self):
        from eden_shell.word_woodland_model import WordWoodland

        game = WordWoodland(random.Random(2))
        round_ = game.new_round()
        self.assertTrue(game.answer(round_.answer))
        self.assertFalse(game.answer(next(v for v in round_.choices if v != round_.answer)))
        self.assertNotIn('score', game.__dict__)

    def test_answer_requires_a_started_round(self):
        from eden_shell.word_woodland_model import WordWoodland

        with self.assertRaises(RuntimeError):
            WordWoodland().answer('S')

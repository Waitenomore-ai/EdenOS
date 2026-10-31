import random
import unittest


class NumberMeadowTests(unittest.TestCase):
    def test_round_has_four_unique_choices_including_answer(self):
        from eden_shell.number_meadow_model import NumberMeadow

        game = NumberMeadow(random.Random(4))
        round_ = game.new_round()
        self.assertEqual(len(round_.choices), 4)
        self.assertEqual(len(set(round_.choices)), 4)
        self.assertIn(round_.count, round_.choices)
        self.assertTrue(all(1 <= value <= 10 for value in round_.choices))

    def test_answers_are_checked_without_persisting_child_data(self):
        from eden_shell.number_meadow_model import NumberMeadow

        game = NumberMeadow(random.Random(1))
        round_ = game.new_round()
        self.assertTrue(game.answer(round_.count))
        self.assertFalse(game.answer(next(value for value in round_.choices if value != round_.count)))
        self.assertNotIn('name', game.__dict__)
        self.assertNotIn('score', game.__dict__)

    def test_answer_requires_a_started_round(self):
        from eden_shell.number_meadow_model import NumberMeadow

        with self.assertRaises(RuntimeError):
            NumberMeadow().answer(1)

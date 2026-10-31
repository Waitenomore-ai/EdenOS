import random
import unittest


class PuzzlePondTests(unittest.TestCase):
    def test_board_has_four_pairs_and_no_score_or_timer(self):
        from eden_shell.puzzle_pond_model import PuzzlePond

        game = PuzzlePond(random.Random(4))
        self.assertEqual(len(game.cards), 8)
        self.assertEqual(sorted(card.symbol for card in game.cards), sorted(["🐸", "🐟", "🦋", "🌼"] * 2))
        self.assertFalse(game.complete)
        self.assertNotIn("score", game.__dict__)
        self.assertNotIn("timer", game.__dict__)

    def test_matching_pair_is_marked_and_mismatch_can_be_hidden(self):
        from eden_shell.puzzle_pond_model import PuzzlePond

        game = PuzzlePond(random.Random(1))
        first = 0
        second = next(i for i in range(1, 8) if game.cards[i].symbol == game.cards[first].symbol)
        self.assertEqual(game.choose(first), "first")
        self.assertEqual(game.choose(second), "matched")
        self.assertTrue(game.cards[first].matched)
        self.assertTrue(game.cards[second].matched)

    def test_choice_before_start_is_not_needed_and_restart_resets(self):
        from eden_shell.puzzle_pond_model import PuzzlePond

        game = PuzzlePond(random.Random(2))
        game.choose(0)
        game.restart()
        self.assertIsNone(game.first)
        self.assertIsNone(game.second)
        self.assertTrue(all(not card.revealed and not card.matched for card in game.cards))

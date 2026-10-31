import unittest

from eden_shell.feelings_model import FeelingsSpace, FEELINGS, CALM_ACTIONS


class FeelingsSpaceTests(unittest.TestCase):
    def test_starts_without_a_mood_or_completed_action(self):
        space = FeelingsSpace()
        self.assertIsNone(space.mood)
        self.assertEqual(space.completed_count, 0)
        self.assertEqual(len(FEELINGS), 4)
        self.assertEqual(len(CALM_ACTIONS), 3)

    def test_selects_a_mood_and_toggles_actions(self):
        space = FeelingsSpace()
        self.assertTrue(space.choose_mood("quiet"))
        self.assertEqual(space.mood.key, "quiet")
        self.assertFalse(space.choose_mood("unknown"))
        self.assertTrue(space.toggle_action(0))
        self.assertFalse(space.toggle_action(0))
        self.assertEqual(space.completed_count, 0)

    def test_reset_clears_mood_and_actions(self):
        space = FeelingsSpace()
        space.choose_mood("worried")
        space.toggle_action(1)
        space.reset()
        self.assertIsNone(space.mood)
        self.assertEqual(space.completed_count, 0)


if __name__ == "__main__":
    unittest.main()

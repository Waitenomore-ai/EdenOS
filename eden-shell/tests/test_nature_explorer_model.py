import unittest

from eden_shell.nature_explorer_model import NatureExplorer, NATURE_ITEMS


class NatureExplorerTests(unittest.TestCase):
    def test_starts_at_first_item_and_exposes_safe_cards(self):
        explorer = NatureExplorer()
        self.assertEqual(explorer.current_index, 0)
        self.assertEqual(explorer.current, NATURE_ITEMS[0])
        self.assertEqual(len(NATURE_ITEMS), 6)
        self.assertTrue(all(item.symbol and item.label for item in NATURE_ITEMS))

    def test_navigation_wraps_around_the_small_card_set(self):
        explorer = NatureExplorer()
        self.assertEqual(explorer.previous().label, NATURE_ITEMS[-1].label)
        self.assertEqual(explorer.next().label, NATURE_ITEMS[0].label)
        self.assertEqual(explorer.next().label, NATURE_ITEMS[1].label)

    def test_marking_current_card_found_is_idempotent_and_resettable(self):
        explorer = NatureExplorer()
        self.assertTrue(explorer.mark_found())
        self.assertFalse(explorer.mark_found())
        self.assertEqual(explorer.found_count, 1)
        explorer.next()
        explorer.mark_found()
        self.assertEqual(explorer.found_count, 2)
        explorer.reset()
        self.assertEqual(explorer.found_count, 0)
        self.assertFalse(explorer.is_found)


if __name__ == "__main__":
    unittest.main()

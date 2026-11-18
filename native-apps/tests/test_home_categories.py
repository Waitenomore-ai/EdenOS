"""The native launcher follows the running iMac's Play/Learn/Create categorisation."""
import unittest
from eden_native.home_categories import HOME_CATEGORIES, activities_in_category


class HomeCategoryTests(unittest.TestCase):
    def test_approved_imac_category_order(self):
        self.assertEqual(tuple(HOME_CATEGORIES), ("play", "learn", "create"))

    def test_imac_story_and_games_are_in_play(self):
        self.assertEqual(activities_in_category("play"), (
            "story-garden", "puzzle-pond", "nature-explorer", "feelings"))

    def test_imac_learning_and_creation_routes(self):
        self.assertEqual(activities_in_category("learn"), ("number-meadow", "word-woodland", "my-day"))
        self.assertEqual(activities_in_category("create"), ("art-studio",))


if __name__ == "__main__":
    unittest.main()

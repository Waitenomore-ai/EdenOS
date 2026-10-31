import unittest


class StoryGardenTests(unittest.TestCase):
    def test_story_has_four_ordered_scenes(self):
        from eden_shell.story_garden_model import StoryGarden

        story = StoryGarden()
        self.assertEqual(story.position, 0)
        self.assertFalse(story.finished)
        scenes = [story.scene]
        for _ in range(3):
            scenes.append(story.next_scene())
        self.assertEqual(len(scenes), 4)
        self.assertTrue(story.finished)
        self.assertEqual(story.next_scene(), scenes[-1])

    def test_story_can_restart_without_persisting_personal_data(self):
        from eden_shell.story_garden_model import StoryGarden

        story = StoryGarden()
        story.next_scene()
        story.next_scene()
        story.restart()
        self.assertEqual(story.position, 0)
        self.assertNotIn('name', story.__dict__)
        self.assertNotIn('score', story.__dict__)

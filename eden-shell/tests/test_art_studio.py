import unittest


class ArtStudioTests(unittest.TestCase):
    def test_board_adds_and_undoes_stamps(self):
        from eden_shell.art_studio_model import ArtBoard

        board = ArtBoard(limit=2)
        self.assertTrue(board.add("🌼", "yellow"))
        self.assertTrue(board.add("⭐", "blue"))
        self.assertFalse(board.add("🦋", "green"))
        self.assertEqual(board.undo().symbol, "⭐")
        self.assertEqual(len(board.stamps), 1)

    def test_clear_removes_only_local_picture_data(self):
        from eden_shell.art_studio_model import ArtBoard

        board = ArtBoard()
        board.add("🌳", "green")
        board.clear()
        self.assertEqual(board.stamps, [])
        self.assertNotIn("name", board.__dict__)
        self.assertNotIn("score", board.__dict__)

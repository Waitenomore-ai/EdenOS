import tempfile, unittest
from pathlib import Path
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from eden_native.art_canvas import ArtCanvas

class ArtCanvasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.canvas = ArtCanvas()
        self.canvas.resize(500, 300)
        self.canvas.show()
        self.app.processEvents()

    def tearDown(self):
        self.canvas.close()

    def test_draw_undo_redo_and_export(self):
        QTest.mousePress(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(30, 30))
        QTest.mouseRelease(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 90))
        self.assertEqual(len(self.canvas.strokes), 1)
        self.canvas.undo()
        self.assertEqual(len(self.canvas.strokes), 0)
        self.canvas.redo()
        self.assertEqual(len(self.canvas.strokes), 1)
        with tempfile.TemporaryDirectory() as tmp:
            output = self.canvas.save_png(Path(tmp))
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 100)
        self.canvas.clear()
        self.assertEqual(len(self.canvas.strokes), 0)

    def test_colour_validation(self):
        self.canvas.set_colour("Purple")
        self.assertEqual(self.canvas.colour, "Purple")
        with self.assertRaises(ValueError):
            self.canvas.set_colour("Invisible")

    def test_editable_project_roundtrip_and_corrupt_input(self):
        QTest.mousePress(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(40, 40))
        QTest.mouseRelease(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 90))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            saved = self.canvas.save_project(directory, ["sticker_apple"])
            self.assertTrue(saved.is_file())
            self.canvas.clear()
            self.assertEqual(self.canvas.load_project(directory), ["sticker_apple"])
            self.assertEqual(len(self.canvas.strokes), 1)
            saved.write_text('{"version":1,"strokes":[{"colour":"Black","width":6,"points":[[999,1]]}],"stickers":[]}')
            with self.assertRaises(ValueError):
                self.canvas.load_project(directory)
            self.assertEqual(len(self.canvas.strokes), 1)

    def test_brush_size_and_eraser_roundtrip(self):
        self.canvas.set_brush_width(12)
        self.canvas.set_eraser()
        QTest.mousePress(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(40, 40))
        QTest.mouseRelease(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 90))
        self.assertEqual(self.canvas.strokes[0]["mode"], "erase")
        self.assertEqual(self.canvas.strokes[0]["width"], 12)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.canvas.save_project(directory)
            self.canvas.clear()
            self.canvas.load_project(directory)
            self.assertEqual(self.canvas.strokes[0]["mode"], "erase")
        self.canvas.set_colour("Blue")
        self.assertEqual(self.canvas.brush_mode, "paint")

    def test_background_saved_and_validated(self):
        self.canvas.set_background("Sky")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            saved = self.canvas.save_project(directory)
            self.canvas.set_background("White")
            self.canvas.load_project(directory)
            self.assertEqual(self.canvas.background.name(), "#e4f2ff")
            import json
            payload = json.loads(saved.read_text())
            payload["background"] = "../not-a-background"
            saved.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                self.canvas.load_project(directory)

    def test_sticker_drag_and_saved_position(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1] / 'assets' / 'stickers'
        manifest = json.loads((root / 'manifest.json').read_text())
        apple = next(item for item in manifest['items'] if item['sku'] == 'sticker_apple')
        self.canvas.set_stickers([root / apple['filename']])
        original = self.canvas.sticker_positions[0][:]
        start = QPoint(round(original[0]*500)+15, round(original[1]*300)+15)
        finish = QPoint(230, 140)
        QTest.mousePress(self.canvas, Qt.MouseButton.LeftButton, pos=start)
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent, QPointF
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(finish), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        self.app.sendEvent(self.canvas, event)
        QTest.mouseRelease(self.canvas, Qt.MouseButton.LeftButton, pos=finish)
        self.assertNotEqual(self.canvas.sticker_positions[0], original)
        self.assertEqual(len(self.canvas.strokes), 0)
        moved = self.canvas.sticker_positions[0][:]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.canvas.save_project(directory, ['sticker_apple'])
            self.canvas.sticker_positions.clear()
            self.assertEqual(self.canvas.load_project(directory), ['sticker_apple'])
            self.assertEqual(self.canvas.sticker_positions[0], moved)

    def test_rejects_corrupt_sticker_coordinates_without_mutation(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            saved = self.canvas.save_project(directory)
            before = self.canvas.sticker_positions[:]
            payload = json.loads(saved.read_text())
            payload['stickers'] = ['sticker_apple']
            payload['sticker_positions'] = [[-1, 2]]
            saved.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                self.canvas.load_project(directory)
            self.assertEqual(self.canvas.sticker_positions, before)

    def test_keyboard_sticker_selection_and_arrow_movement(self):
        import json
        root = Path(__file__).resolve().parents[1] / 'assets' / 'stickers'
        manifest = json.loads((root / 'manifest.json').read_text())
        apple = next(item for item in manifest['items'] if item['sku'] == 'sticker_apple')
        self.canvas.set_stickers([root / apple['filename']])
        self.canvas.setFocus()
        QTest.keyClick(self.canvas, Qt.Key.Key_1)
        self.assertEqual(self.canvas.selected_sticker, 0)
        before = self.canvas.sticker_positions[0][:]
        QTest.keyClick(self.canvas, Qt.Key.Key_Right)
        self.assertGreater(self.canvas.sticker_positions[0][0], before[0])
        QTest.keyClick(self.canvas, Qt.Key.Key_Down)
        self.assertGreater(self.canvas.sticker_positions[0][1], before[1])
        self.assertEqual(len(self.canvas.strokes), 0)

    def test_reward_locked_sticker_cannot_load_without_entitlement(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            self.canvas.save_project(directory)
            self.canvas.set_background('Sky')
            path=directory/'current-art-project.json'
            payload=json.loads(path.read_text())
            payload['stickers']=['sticker_owl']
            payload['sticker_positions']=[[.3,.3]]
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                self.canvas.load_project(directory,allowed_stickers={'sticker_apple'})
            self.assertEqual(self.canvas.background.name(),'#e4f2ff')
            self.assertEqual(self.canvas.sticker_positions,[])

    def test_canonical_imac_brush_sizes(self):
        for width in (3,4,13,20):
            self.canvas.set_brush_width(width)
            self.assertEqual(self.canvas.stroke_width,width)

    def test_sticker_layer_reorder_preserves_coordinates(self):
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        manifest=json.loads((root/'manifest.json').read_text())
        by_sku={item['sku']:root/item['filename'] for item in manifest['items']}
        self.canvas.set_stickers([by_sku['sticker_apple'],by_sku['sticker_butterfly']])
        self.canvas.sticker_positions=[[.1,.2],[.4,.5]]
        self.canvas.selected_sticker=0
        self.assertTrue(self.canvas.move_selected_sticker_layer(1))
        self.assertEqual(self.canvas.sticker_paths[1],by_sku['sticker_apple'])
        self.assertEqual(self.canvas.sticker_positions[1],[.1,.2])
        self.assertEqual(self.canvas.selected_sticker,1)
        self.assertFalse(self.canvas.move_selected_sticker_layer(1))
        self.assertTrue(self.canvas.move_selected_sticker_layer(-1))
        self.assertEqual(self.canvas.sticker_paths[0],by_sku['sticker_apple'])
        with self.assertRaises(ValueError):self.canvas.move_selected_sticker_layer(4)

    def test_sticker_layer_order_roundtrips_with_skus(self):
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        manifest=json.loads((root/'manifest.json').read_text())
        by_sku={item['sku']:root/item['filename'] for item in manifest['items']}
        self.canvas.set_stickers([by_sku['sticker_apple'],by_sku['sticker_butterfly']],['sticker_apple','sticker_butterfly'])
        self.canvas.selected_sticker=0
        self.assertTrue(self.canvas.move_selected_sticker_layer(1))
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            self.canvas.save_project(directory,['sticker_apple','sticker_butterfly'])
            self.assertEqual(self.canvas.load_project(directory,allowed_stickers={'sticker_apple','sticker_butterfly'}),['sticker_butterfly','sticker_apple'])

    def test_keyboard_selection_move_and_layer_change(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        by_sku={item['sku']:root/item['filename'] for item in json.loads((root/'manifest.json').read_text())['items']}
        self.canvas.set_stickers([by_sku['sticker_apple'],by_sku['sticker_butterfly']],['sticker_apple','sticker_butterfly'])
        self.canvas.show()
        QApplication.processEvents()
        self.canvas.setFocus()
        QTest.keyClick(self.canvas,Qt.Key.Key_1)
        self.assertEqual(self.canvas.selected_sticker,0)
        before=self.canvas.sticker_positions[0][0]
        QTest.keyClick(self.canvas,Qt.Key.Key_Right)
        self.assertGreater(self.canvas.sticker_positions[0][0],before)
        QTest.keyClick(self.canvas,Qt.Key.Key_PageUp)
        self.assertEqual(self.canvas.selected_sticker,1)
        self.assertEqual(self.canvas.sticker_skus,['sticker_butterfly','sticker_apple'])
        QTest.keyClick(self.canvas,Qt.Key.Key_PageDown)
        self.assertEqual(self.canvas.selected_sticker,0)
        self.canvas.hide()

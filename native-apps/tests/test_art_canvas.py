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

    def test_failed_undo_preserves_history_for_recovery(self):
        self.canvas._record_action('sticker_move',(0,[.1,.1],[.2,.2]))
        self.assertFalse(self.canvas.undo_action())
        self.assertEqual(len(self.canvas.action_undo),1)
        self.assertEqual(len(self.canvas.action_redo),0)
        self.canvas.sticker_positions.append([.2,.2])
        self.assertTrue(self.canvas.undo_action())
        self.assertEqual(self.canvas.sticker_positions[0],[.1,.1])

    def test_keyboard_shortcuts_undo_redo_combined_actions(self):
        QTest.mousePress(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(30, 30))
        QTest.mouseRelease(self.canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 90))
        self.assertEqual(len(self.canvas.strokes),1)
        self.canvas.setFocus()
        QTest.keyClick(self.canvas, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(len(self.canvas.strokes),0)
        QTest.keyClick(self.canvas, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(len(self.canvas.strokes),1)
        QTest.keyClick(self.canvas, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(self.canvas, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(len(self.canvas.strokes),1)

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

    def test_picture_save_skips_existing_and_dangling_symlink_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            first=directory/'eden-art-0001.png'
            first.write_bytes(b'preserve-existing-picture')
            second=directory/'eden-art-0002.png'
            second.symlink_to(directory/'missing-private-file.png')
            saved=self.canvas.save_png(directory)
            self.assertEqual(saved.name,'eden-art-0003.png')
            self.assertEqual(first.read_bytes(),b'preserve-existing-picture')
            self.assertTrue(second.is_symlink())
            self.assertFalse((directory/'missing-private-file.png').exists())
            self.assertGreater(saved.stat().st_size,100)
            self.assertEqual(sorted(x.name for x in directory.iterdir()),['eden-art-0001.png','eden-art-0002.png','eden-art-0003.png'])

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

    def test_rejects_nonfinite_and_boolean_project_coordinates_without_mutation(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            project=self.canvas.save_project(directory)
            original_strokes=self.canvas.strokes[:]
            cases=[
                {'version':1,'strokes':[{'colour':'Blue','width':True,'points':[[.1,.2]]}],'stickers':[]},
                {'version':1,'strokes':[{'colour':'Blue','width':6,'points':[]}],'stickers':[]},
                {'version':1,'strokes':[{'colour':'Blue','width':6,'points':[[True,.2]]}],'stickers':[]},
                {'version':1,'strokes':[{'colour':'Blue','width':6,'points':[[float('nan'),.2]]}],'stickers':[]},
                {'version':1,'strokes':[],'stickers':['sticker_apple'],'sticker_positions':[[float('inf'),.2]]},
            ]
            for payload in cases:
                project.write_text(json.dumps(payload))
                with self.subTest(payload=payload),self.assertRaises(ValueError):
                    self.canvas.load_project(directory)
                self.assertEqual(self.canvas.strokes,original_strokes)

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

    def test_duplicate_sticker_entitlement_counts_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.canvas.sticker_skus = ['sticker_apple', 'sticker_apple']
            self.canvas.sticker_positions = [[.1,.1],[.3,.3]]
            with self.assertRaisesRegex(ValueError, 'entitlement mismatch'):
                self.canvas.save_project(Path(tmp), ['sticker_apple', 'sticker_butterfly'])
            self.assertFalse((Path(tmp)/'current-art-project.json').exists())

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

    def test_sticker_keyboard_move_undo_redo_and_layer_history_invalidation(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        by_sku={item['sku']:root/item['filename'] for item in json.loads((root/'manifest.json').read_text())['items']}
        self.canvas.set_stickers([by_sku['sticker_apple'],by_sku['sticker_butterfly']],['sticker_apple','sticker_butterfly'])
        self.canvas.show();self.app.processEvents();self.canvas.setFocus()
        QTest.keyClick(self.canvas,Qt.Key.Key_1)
        before=self.canvas.sticker_positions[0][:]
        QTest.keyClick(self.canvas,Qt.Key.Key_Right)
        moved=self.canvas.sticker_positions[0][:]
        self.assertNotEqual(before,moved)
        self.assertTrue(self.canvas.undo_sticker_move())
        self.assertEqual(self.canvas.sticker_positions[0],before)
        self.assertTrue(self.canvas.redo_sticker_move())
        self.assertEqual(self.canvas.sticker_positions[0],moved)
        QTest.keyClick(self.canvas,Qt.Key.Key_PageUp)
        self.assertFalse(self.canvas.undo_sticker_move())
        self.canvas.hide()

    def test_specialised_undo_respects_mixed_action_chronology(self):
        QTest.mousePress(self.canvas,Qt.MouseButton.LeftButton,pos=QPoint(30,30))
        QTest.mouseRelease(self.canvas,Qt.MouseButton.LeftButton,pos=QPoint(100,90))
        self.canvas.set_background('Sky')
        self.assertFalse(self.canvas.undo())
        self.assertEqual(len(self.canvas.strokes),1)
        self.assertEqual(len(self.canvas.action_undo),2)
        self.assertTrue(self.canvas.undo_action())
        self.assertTrue(self.canvas.undo())
        self.assertEqual(len(self.canvas.strokes),0)
        self.assertTrue(self.canvas.redo())
        self.assertEqual(len(self.canvas.strokes),1)
        self.assertTrue(self.canvas.redo_action())
        self.assertEqual(self.canvas.background.name(),'#e4f2ff')
        self.assertFalse(self.canvas.undo_sticker_move())

    def test_unified_history_tracks_background_changes_and_redo_invalidation(self):
        self.assertEqual(self.canvas.background.name(),'#ffffff')
        self.canvas.set_background('Sky')
        self.canvas.set_background('Grass')
        self.assertEqual(self.canvas.background.name(),'#e8f7e7')
        self.assertTrue(self.canvas.undo_action())
        self.assertEqual(self.canvas.background.name(),'#e4f2ff')
        self.assertTrue(self.canvas.undo_action())
        self.assertEqual(self.canvas.background.name(),'#ffffff')
        self.assertTrue(self.canvas.redo_action())
        self.assertEqual(self.canvas.background.name(),'#e4f2ff')
        self.canvas.set_background('Peach')
        self.assertFalse(self.canvas.redo_action())
        self.assertEqual(self.canvas.background.name(),'#fff0dc')

    def test_unified_history_reverses_interleaved_stroke_and_sticker_move(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        apple=next(item for item in json.loads((root/'manifest.json').read_text())['items'] if item['sku']=='sticker_apple')
        self.canvas.set_stickers([root/apple['filename']],['sticker_apple'])
        stroke={'colour':'Blue','width':6,'points':[[.1,.1],[.2,.2]],'mode':'paint'}
        self.canvas.strokes.append(stroke)
        self.canvas._record_action('stroke',stroke)
        self.canvas.show();self.app.processEvents();self.canvas.setFocus()
        QTest.keyClick(self.canvas,Qt.Key.Key_1)
        before=self.canvas.sticker_positions[0][:]
        QTest.keyClick(self.canvas,Qt.Key.Key_Right)
        after=self.canvas.sticker_positions[0][:]
        self.assertTrue(self.canvas.undo_action())
        self.assertEqual(self.canvas.sticker_positions[0],before)
        self.assertEqual(len(self.canvas.strokes),1)
        self.assertTrue(self.canvas.undo_action())
        self.assertEqual(len(self.canvas.strokes),0)
        self.assertTrue(self.canvas.redo_action())
        self.assertEqual(self.canvas.strokes,[stroke])
        self.assertTrue(self.canvas.redo_action())
        self.assertEqual(self.canvas.sticker_positions[0],after)
        self.assertFalse(self.canvas.redo_action())
        self.canvas.hide()

    def test_drag_sticker_undo_redo(self):
        from PySide6.QtCore import Qt,QPoint
        from PySide6.QtTest import QTest
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent,QPointF
        import json
        root=Path(__file__).resolve().parents[1]/'assets'/'stickers'
        apple=next(item for item in json.loads((root/'manifest.json').read_text())['items'] if item['sku']=='sticker_apple')
        self.canvas.set_stickers([root/apple['filename']],['sticker_apple'])
        before=self.canvas.sticker_positions[0][:]
        start=QPoint(round(before[0]*500)+10,round(before[1]*300)+10)
        QTest.mousePress(self.canvas,Qt.MouseButton.LeftButton,pos=start)
        move=QMouseEvent(QEvent.Type.MouseMove,QPointF(210,145),Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier)
        self.app.sendEvent(self.canvas,move)
        QTest.mouseRelease(self.canvas,Qt.MouseButton.LeftButton,pos=QPoint(210,145))
        after=self.canvas.sticker_positions[0][:]
        self.assertNotEqual(before,after)
        self.assertTrue(self.canvas.undo_sticker_move())
        self.assertEqual(self.canvas.sticker_positions[0],before)
        self.assertTrue(self.canvas.redo_sticker_move())
        self.assertEqual(self.canvas.sticker_positions[0],after)

    def test_eraser_reveals_new_background_not_old_background_colour(self):
        from PySide6.QtGui import QColor
        self.canvas.strokes = [
            {'colour':'Blue','width':20,'points':[[.1,.5],[.9,.5]],'mode':'paint'},
            {'colour':'Blue','width':24,'points':[[.5,.4],[.5,.6]],'mode':'erase'},
        ]
        self.canvas.set_background('Sky')
        self.app.processEvents()
        image=self.canvas.grab().toImage()
        centre=image.pixelColor(250,150)
        side=image.pixelColor(120,150)
        self.assertEqual(centre.name(),QColor('#e4f2ff').name())
        self.assertEqual(side.name(),QColor('#2964d4').name())
        self.canvas.set_background('Peach')
        self.app.processEvents()
        self.assertEqual(self.canvas.grab().toImage().pixelColor(250,150).name(),QColor('#fff0dc').name())

import tempfile,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication,QPushButton
from eden_native.core import detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter
from eden_native.qt_app import create_window
from eden_native.approved_models.art_studio_model import ArtBoard
SOURCE=Path(__file__).resolve().parents[1] / 'eden_native' / 'approved_models' / 'parent_pin.py'
class ArtStudioTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  plat=detect_platform('linux',Path(self.tmp.name),{'XDG_DATA_HOME':self.tmp.name+'/data','XDG_CONFIG_HOME':self.tmp.name+'/config'})
  repo=ProfileRepository(plat);repo.create('eden_demo','Eden Demo','approved-eden')
  pin=ApprovedPinAdapter(plat,SOURCE);pin.set_pin('1234')
  self.window=create_window(pin_adapter=pin,profiles=repo);self.window.show();self.app.processEvents()
 def tearDown(self):self.window.close();self.app.processEvents();self.tmp.cleanup()
 def click(self,label):
  found=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.isVisible() and b.text()==label]
  self.assertEqual(len(found),1,label);found[0].click();self.app.processEvents()
 def test_sticker_garden_places_and_removes_only_unlocked_stickers(self):
  from eden_native.sticker_garden import load_garden
  from PySide6.QtWidgets import QPushButton
  self.click('Eden Demo');self.click('My Sticker Garden')
  self.assertEqual(self.window.state.page,'sticker-garden')
  self.assertFalse(self.window.select_garden_sticker('sticker_acorn'))
  self.assertFalse(self.window.place_garden_sticker(0))
  self.assertFalse(self.window.remove_garden_sticker(0))
  self.click('Apple')
  slots=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.objectName()=='stickerGardenSlot' and b.isVisible()]
  self.assertEqual(len(slots),24)
  slots[0].click();self.app.processEvents()
  path=self.window.sticker_garden_path()
  self.assertEqual(load_garden(path,{'sticker_apple'}),{0:'sticker_apple'})
  self.assertFalse(self.window.place_garden_sticker(24))
  self.click('Remove selected')
  self.assertEqual(load_garden(path,{'sticker_apple'}),{})
  self.window.transition(self.window.state.logout())
  self.assertFalse(self.window.place_garden_sticker(0))

 def test_sticker_garden_three_panel_layout_and_category_filter(self):
  from PySide6.QtWidgets import QWidget,QComboBox,QPushButton
  self.click('Eden Demo');self.click('My Sticker Garden')
  root=self.window.controls_widget
  self.assertEqual(len(root.findChildren(QWidget,'stickerGardenThreePanel')),1)
  self.assertEqual(len(root.findChildren(QWidget,'stickerGardenPickerPanel')),1)
  self.assertEqual(len(root.findChildren(QWidget,'stickerGardenCentrePanel')),1)
  self.assertEqual(len(root.findChildren(QWidget,'stickerGardenActionsPanel')),1)
  combo=root.findChild(QComboBox,'stickerGardenCategory')
  self.assertEqual(combo.currentText(),'All')
  self.assertTrue(self.window.select_garden_category('Nature'))
  combo=self.window.controls_widget.findChildren(QComboBox,'stickerGardenCategory')[-1]
  self.assertEqual(combo.currentText(),'Nature')
  self.assertFalse(self.window.select_garden_category('Not a category'))
  board=self.window.controls_widget.findChildren(QWidget,'stickerGardenBoard')[-1]
  self.assertEqual(board.layout().count(),24)
  self.assertTrue(board.property("approvedGardenBackground").endswith("garden-background-v58.webp"))

 def test_sticker_garden_move_and_confirmed_clear(self):
  from eden_native.sticker_garden import load_garden
  self.click('Eden Demo');self.click('My Sticker Garden');self.click('Apple')
  self.assertTrue(self.window.place_garden_sticker(7))
  path=self.window.sticker_garden_path()
  self.assertFalse(self.window.move_garden_sticker(-1,0) if self.window.garden_selected_slot is None else self.window.move_garden_sticker(-1,-1))
  self.assertTrue(self.window.move_garden_sticker(1,0))
  self.assertEqual(load_garden(path,{'sticker_apple'}),{8:'sticker_apple'})
  self.assertTrue(self.window.place_garden_sticker(9))
  self.assertFalse(self.window.move_garden_sticker(-1,0))
  self.assertEqual(load_garden(path,{'sticker_apple'}),{8:'sticker_apple',9:'sticker_apple'})
  self.assertFalse(self.window.clear_sticker_garden())
  self.assertEqual(len(load_garden(path,{'sticker_apple'})),2)
  self.assertTrue(self.window.clear_sticker_garden())
  self.assertEqual(load_garden(path,{'sticker_apple'}),{})

 def test_sticker_garden_persists_between_visits(self):
  from eden_native.sticker_garden import load_garden
  self.click('Eden Demo');self.click('My Sticker Garden');self.click('Apple')
  self.assertTrue(self.window.place_garden_sticker(7))
  path=self.window.sticker_garden_path()
  self.window.transition(self.window.state.logout());self.app.processEvents();self.click('Eden Demo');self.click('My Sticker Garden')
  self.assertEqual(load_garden(path,{'sticker_apple'}),{7:'sticker_apple'})
  self.assertFalse(self.window.select_garden_sticker('sticker_acorn'))

 def test_parent_sticker_unlock_requires_verified_pin(self):
  from eden_native.garden_stars import GardenStars
  self.click('Eden Demo')
  self.assertFalse(self.window.parent_unlock_sticker())
  self.click('Parent Corner')
  self.assertFalse(self.window.parent_unlock_sticker())
  self.window.pin_input.setText('1234')
  self.click('Unlock Parent Corner')
  self.assertTrue(self.window.state.parent_unlocked)
  self.window.parent_reward_combo.setCurrentIndex(1)
  self.assertEqual(self.window.parent_reward_combo.currentData(),'sticker_acorn')
  self.click('Parent unlock selected sticker')
  service=GardenStars(self.window.profiles.path.parent/'garden-stars.sqlite3')
  self.assertIn('sticker_acorn',{item['sku'] for item in service.collection('eden_demo')})
  self.assertEqual(service.balance('eden_demo'),0)
  self.click('Back to child home')
  self.assertFalse(self.window.parent_unlock_sticker())
  self.click('Art Studio');self.click('Sticker: Acorn')
  self.assertEqual(self.window.art_canvas.sticker_skus,['sticker_acorn'])

 def test_garden_stars_awards_on_correct_answers_only(self):
  from eden_native.garden_stars import GardenStars
  self.click('Eden Demo');self.click('Number Meadow')
  service=GardenStars(self.window.profiles.path.parent/'garden-stars.sqlite3')
  self.assertEqual(service.balance('eden_demo'),0)
  game=self.window.number_game
  wrong=next(v for v in game.round.choices if v!=game.round.count)
  self.window.answer_number(wrong)
  self.assertEqual(service.balance('eden_demo'),0)
  self.window.answer_number(game.round.count)
  self.assertEqual(service.balance('eden_demo'),10)
  self.window.toolbar_home.click();self.app.processEvents();self.click('Word Woodland')
  game=self.window.word_game
  self.window.answer_word(game.round.answer)
  self.assertEqual(service.balance('eden_demo'),20)

 def test_saved_picture_gallery_is_child_scoped_and_ignores_symlinks(self):
  self.click('Eden Demo');self.click('Art Studio');self.click('Save picture')
  directory=self.window.profiles.path.parent/'art-studio'/'eden_demo'
  self.assertTrue((directory/'eden-art-0001.png').is_file())
  (directory/'eden-art-0002.png').symlink_to(directory/'eden-art-0001.png')
  self.window.toolbar_home.click();self.app.processEvents()
  self.click('My saved pictures')
  self.assertEqual(self.window.state.page,'my-artwork')
  self.assertFalse(self.window.select_artwork('eden-art-0002.png'))
  self.assertFalse(self.window.select_artwork('../eden-art-0001.png'))
  self.click('eden-art-0001.png')
  self.assertEqual(self.window.artwork_preview,'eden-art-0001.png')
  self.click('Back to home')
  self.assertFalse(self.window.select_artwork('eden-art-0001.png'))

 def test_puzzle_completion_and_saved_art_award_stars(self):
  from eden_native.garden_stars import GardenStars
  self.click('Eden Demo');self.click('Puzzle Pond')
  service=GardenStars(self.window.profiles.path.parent/'garden-stars.sqlite3')
  game=self.window.puzzle_game
  pairs={}
  for card in game.cards:
   pairs.setdefault(card.symbol,[]).append(card.index)
  for first,second in pairs.values():
   self.window.choose_puzzle(first)
   self.window.choose_puzzle(second)
  self.assertTrue(game.complete)
  self.assertEqual(service.balance('eden_demo'),10)
  self.window.toolbar_home.click();self.app.processEvents()
  self.click('Art Studio');self.click('Save picture')
  self.assertEqual(service.balance('eden_demo'),20)

 def test_free_emoji_stamps_survive_approved_sticker_undo(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Add 🌼')
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['🌼'])
  self.click('Sticker: Apple')
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['🌼','sticker_apple'])
  self.assertTrue(self.window.art_canvas.undo_action())
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['🌼'])
  self.assertTrue(self.window.art_canvas.redo_action())
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['🌼','sticker_apple'])

 def test_garden_stars_shop_uses_approved_png_icons_and_accessible_tiles(self):
  from PySide6.QtWidgets import QPushButton
  self.click('Eden Demo');self.click('My Garden Stars')
  tiles=[b for b in self.window.controls_widget.findChildren(QPushButton) if b.objectName()=='gardenStarsStickerTile']
  self.assertEqual(len(tiles),75)
  apple=next(b for b in tiles if b.text()=='Apple — Collected ✓')
  acorn=next(b for b in tiles if b.text()=='Acorn — 5 stars')
  self.assertFalse(apple.icon().isNull())
  self.assertFalse(acorn.icon().isNull())
  self.assertEqual(acorn.accessibleDescription(),'Unlock for 5 Garden Stars')
  self.assertGreaterEqual(acorn.minimumHeight(),100)

 def test_garden_stars_shop_requires_balance_and_unlocks_only_for_child(self):
  from eden_native.garden_stars import GardenStars
  self.click('Eden Demo');self.click('My Garden Stars')
  self.assertEqual(self.window.state.page,'garden-stars')
  self.assertFalse(self.window.purchase_garden_sticker('sticker_acorn'))
  self.assertFalse(self.window.purchase_garden_sticker('sticker_unknown'))
  self.assertFalse(self.window.purchase_garden_sticker('sticker_acorn'))
  service=GardenStars(self.window.profiles.path.parent/'garden-stars.sqlite3')
  self.assertEqual(service.balance('eden_demo'),0)
  service.earn('eden_demo','number_meadow','test-event-garden-01')
  self.click('Back to home');self.click('My Garden Stars')
  self.click('Acorn — 5 stars')
  self.assertEqual(service.balance('eden_demo'),5)
  self.assertIn('sticker_acorn',{item['sku'] for item in service.collection('eden_demo')})
  self.click('Back to home');self.click('Art Studio')
  self.click('Sticker: Acorn')
  self.assertEqual(self.window.art_canvas.sticker_skus,['sticker_acorn'])

 def test_garden_stars_purchase_rejects_non_shop_context(self):
  self.click('Eden Demo')
  self.assertFalse(self.window.purchase_garden_sticker('sticker_acorn'))
  self.assertFalse(self.window.open_garden_stars() if self.window.state.page!='home' else self.window.purchase_garden_sticker('sticker_acorn'))

 def test_stamps_undo_redo_clear(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.assertIsInstance(self.window.art_game,ArtBoard)
  self.click('Sticker: Apple');self.assertEqual(len(self.window.art_game.stamps),1)
  self.assertEqual(len(self.window.art_canvas.sticker_paths),1)
  self.assertTrue(self.window.art_canvas.sticker_paths[0].is_file())
  self.click('Undo');self.assertEqual(len(self.window.art_game.stamps),0)
  self.click('Redo');self.assertEqual(len(self.window.art_game.stamps),1)
  self.click('Clear');self.assertEqual(len(self.window.art_game.stamps),0)
  self.click('Back to home');self.assertEqual(self.window.state.page,'home')
 def test_render_keeps_combined_history_after_sticker_and_background(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple')
  canvas=self.window.art_canvas
  canvas.set_background('Sky')
  self.window.render()
  self.assertEqual(len(canvas.action_undo),2)
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.background.name(),'#ffffff')
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.sticker_skus,[])
  self.assertTrue(canvas.redo_action())
  self.assertTrue(canvas.redo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple'])
  self.assertEqual(canvas.background.name(),'#e4f2ff')

 def test_remove_selected_sticker_accessible_button(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple');self.click('Sticker: Butterfly')
  self.window.art_canvas.selected_sticker=0
  self.click('Remove selected sticker')
  self.assertEqual(self.window.art_canvas.sticker_skus,['sticker_butterfly'])
  self.assertTrue(self.window.art_canvas.undo_action())
  self.assertEqual(self.window.art_canvas.sticker_skus,['sticker_apple','sticker_butterfly'])

 def test_remove_selected_sticker_from_middle_and_restore_order(self):
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple');self.click('Sticker: Butterfly');self.click('Sticker: Apple')
  canvas=self.window.art_canvas
  canvas.selected_sticker=1
  canvas.setFocus()
  QTest.keyClick(canvas,Qt.Key.Key_Delete)
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],canvas.sticker_skus)
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_butterfly','sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],canvas.sticker_skus)
  self.assertTrue(canvas.redo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_apple'])

 def test_remove_sticker_can_be_undone_and_redone_in_shared_history(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple');self.click('Sticker: Butterfly')
  canvas=self.window.art_canvas
  self.assertTrue(canvas.remove_last_sticker())
  self.assertEqual(canvas.sticker_skus,['sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['sticker_apple'])
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_butterfly'])
  self.assertTrue(canvas.redo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple'])
  self.window.save_art_project()
  import json
  project=self.window.art_project_directory()/'current-art-project.json'
  self.assertEqual(json.loads(project.read_text())['stickers'],['sticker_apple'])

 def test_unified_sticker_add_undo_redo_preserves_model_and_save(self):
  import json
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple')
  canvas=self.window.art_canvas
  self.assertEqual(canvas.sticker_skus,['sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['sticker_apple'])
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.sticker_skus,[])
  self.assertEqual(self.window.art_game.stamps,[])
  self.assertTrue(canvas.redo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],['sticker_apple'])
  self.window.save_art_project()
  project=self.window.art_project_directory()/'current-art-project.json'
  self.assertEqual(json.loads(project.read_text())['stickers'],['sticker_apple'])

 def test_layer_reorder_is_reversible_in_combined_history(self):
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple');self.click('Sticker: Butterfly')
  canvas=self.window.art_canvas
  canvas.selected_sticker=0
  self.assertTrue(canvas.move_selected_sticker_layer(1))
  self.assertEqual(canvas.sticker_skus,['sticker_butterfly','sticker_apple'])
  self.assertTrue(canvas.undo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_butterfly'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],canvas.sticker_skus)
  self.assertTrue(canvas.redo_action())
  self.assertEqual(canvas.sticker_skus,['sticker_butterfly','sticker_apple'])
  self.assertEqual([x.symbol for x in self.window.art_game.stamps],canvas.sticker_skus)

 def test_keyboard_layer_change_syncs_canonical_model_and_saved_project(self):
  import json
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  self.click('Eden Demo');self.click('Art Studio')
  self.click('Sticker: Apple');self.click('Sticker: Butterfly')
  canvas=self.window.art_canvas
  self.assertEqual(canvas.sticker_skus,['sticker_apple','sticker_butterfly'])
  canvas.setFocus()
  QTest.keyClick(canvas,Qt.Key.Key_1)
  QTest.keyClick(canvas,Qt.Key.Key_PageUp)
  self.app.processEvents()
  self.assertEqual(canvas.sticker_skus,['sticker_butterfly','sticker_apple'])
  self.assertEqual([stamp.symbol for stamp in self.window.art_game.stamps],['sticker_butterfly','sticker_apple'])
  self.click('Save editable drawing')
  project=self.window.art_project_directory()/'current-art-project.json'
  self.assertEqual(json.loads(project.read_text())['stickers'],['sticker_butterfly','sticker_apple'])
  self.click('Open saved drawing')
  self.assertEqual([stamp.symbol for stamp in self.window.art_game.stamps],['sticker_butterfly','sticker_apple'])

 def test_editable_project_is_child_scoped(self):
  from PySide6.QtCore import Qt, QPoint
  from PySide6.QtTest import QTest
  self.click('Eden Demo');self.click('Art Studio')
  canvas=self.window.art_canvas
  QTest.mousePress(canvas,Qt.MouseButton.LeftButton,pos=QPoint(40,40))
  QTest.mouseRelease(canvas,Qt.MouseButton.LeftButton,pos=QPoint(90,80))
  self.assertEqual(len(canvas.strokes),1)
  self.click('Sticker: Apple')
  self.click('Save editable drawing')
  project=self.window.art_project_directory()/'current-art-project.json'
  self.assertTrue(project.exists())
  self.click('Clear drawing')
  self.click('Clear')
  self.assertEqual(len(canvas.strokes),0)
  self.click('Open saved drawing')
  self.assertEqual(len(canvas.strokes),1)
  self.assertEqual(len(self.window.art_game.stamps),1)
  self.assertEqual(self.window.art_game.stamps[0].symbol,'sticker_apple')

if __name__=='__main__':unittest.main()

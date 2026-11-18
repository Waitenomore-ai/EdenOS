"""Native Qt Widgets preview. No browser wrapper or production profile access."""
from __future__ import annotations
from pathlib import Path
import json
import os
import uuid
from .core import NavigationState, detect_platform
from .parent_session import ParentSession
from .avatars import resolve_avatar
from .parent_profiles import ParentProfileService
from .approved_models.profile_cards import SELECTABLE_AVATARS
from .activity_preferences import ActivityPreferences, ACTIVITIES
from .approved_models.number_meadow_model import NumberMeadow
from .approved_models.word_woodland_model import WordWoodland
from .approved_models.puzzle_pond_model import PuzzlePond
from .approved_models.nature_explorer_model import NatureExplorer
from .approved_models.feelings_model import FeelingsSpace, FEELINGS, CALM_ACTIONS
from .approved_models.art_studio_model import ArtBoard
from .approved_models.time_routines_model import Routine, ROUTINES
from .approved_models.story_garden_model import StoryGarden, SCENES
from .art_canvas import ArtCanvas, PALETTE, BACKGROUNDS
from .garden_stars import GardenStars
from .sticker_garden import load_garden, save_garden, SLOTS

def create_window(*, pin_adapter=None, profiles=None):
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QScrollArea, QSizePolicy, QGridLayout, QHBoxLayout
    from PySide6.QtCore import Qt, QTimer, QSize, QUrl
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    except ImportError:
        QMediaPlayer = QAudioOutput = None
    from PySide6.QtGui import QPixmap, QIcon

    art_root = Path(__file__).resolve().parent.parent / "assets" / "activities"

    def picture_path(activity, word):
        if not isinstance(word, str): return None
        name = word.lower().replace(" ", "_")
        if not name.replace("_", "").isalnum(): return None
        path = art_root / activity / (name + ".png")
        return path if path.is_file() and not path.is_symlink() else None

    class EdenNativeWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.state = NavigationState()
            self.pin_adapter = pin_adapter
            self.profiles = profiles
            self.session = ParentSession(self.state, pin_adapter.verify_pin) if pin_adapter else None
            self.setWindowTitle("Eden OS — native desktop preview")
            self.resize(1024, 768)
            self.layout = QVBoxLayout(self)
            self.title = QLabel("Eden OS")
            self.title.setObjectName("edenTitle")
            self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.title)
            self.activity_toolbar = QWidget()
            self.activity_toolbar.setObjectName("edenSharedActivityToolbar")
            toolbar_layout = QGridLayout(self.activity_toolbar)
            self.toolbar_home = QPushButton("⌂ Home")
            self.toolbar_home.setObjectName("edenToolbarHome")
            self.toolbar_home.setAccessibleName("Home")
            self.toolbar_home.setMinimumSize(125, 56)
            self.toolbar_home.clicked.connect(lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
            toolbar_layout.addWidget(self.toolbar_home, 0, 0)
            self.toolbar_heading = QLabel("")
            self.toolbar_heading.setObjectName("edenSharedActivityHeading")
            self.toolbar_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.toolbar_heading.setStyleSheet("font-size: 23px; font-weight: bold;")
            toolbar_layout.addWidget(self.toolbar_heading, 0, 1)
            toolbar_layout.addWidget(QWidget(), 0, 2)
            toolbar_layout.setColumnMinimumWidth(2, 125)
            toolbar_layout.setColumnStretch(1, 1)
            self.layout.addWidget(self.activity_toolbar)
            self.info = QLabel()
            self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.info)
            self.avatar_image = QLabel()
            self.avatar_image.setObjectName("selectedAvatarImage")
            self.avatar_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.avatar_image.setMaximumHeight(120)
            self.layout.addWidget(self.avatar_image)
            self.scroll_area = QScrollArea()
            self.scroll_area.setObjectName("edenScrollableControls")
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.scroll_area.setMinimumHeight(100)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.controls_widget = QWidget()
            self.controls_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            self.buttons = QVBoxLayout(self.controls_widget)
            self.scroll_area.setWidget(self.controls_widget)
            self.layout.addWidget(self.scroll_area, 1)
            self.pin_input = None
            self.pin_confirm = None
            self.profile_name = None
            self.profile_username = None
            self.profile_avatar = None
            self.activity_checks = {}
            self.parent_reward_combo = None
            self.artwork_preview = None
            self.garden_selected_sku = None
            self.garden_selected_slot = None
            self.garden_clear_confirm = False
            self.garden_category = "All"
            self.activity_grid = None
            self.number_game = None
            self.word_game = None
            self.puzzle_game = None
            self.puzzle_waiting = False
            self.nature_game = None
            self.feelings_game = None
            self.art_game = None
            self.art_canvas = None
            self.day_game = None
            self.story_game = None
            self.story_books = ()
            self.story_selected = None
            self.story_page = 0
            self.story_audio = None
            self.story_output = None
            self.render()

        def transition(self, state):
            self.state = state
            if self.session: self.session.state = state
            self.render()

        def submit_pin(self):
            if not self.session or not self.pin_input: return
            value = self.pin_input.text()
            self.pin_input.clear()
            accepted = self.session.authenticate(value)
            self.state = self.session.state
            self.render()
            if not accepted: self.info.setText("Incorrect PIN. Parent Corner remains locked.")

        def setup_pin(self):
            # First-time setup is a deliberate demonstration only. No existing PIN may be overwritten.
            if not self.pin_adapter or self.pin_adapter.has_pin() or not self.pin_input: return
            value = self.pin_input.text()
            confirm = self.pin_confirm.text() if self.pin_confirm else None
            self.pin_input.clear()
            if self.pin_confirm: self.pin_confirm.clear()
            if value != confirm:
                self.info.setText("PINs must match.")
                return
            try:
                self.pin_adapter.set_pin(value)
            except (ValueError, OSError):
                self.info.setText("Choose a valid 4–8 digit PIN.")
                return
            self.session.state = self.state.unlock_parent(True)
            self.state = self.session.state
            self.render()

        def create_profile(self):
            if not self.session or not self.profiles or not self.profile_name or not self.profile_username or not self.profile_avatar:
                return
            try:
                ParentProfileService(self.session, self.profiles).create(
                    self.profile_username.text().strip().lower(), self.profile_name.text(), self.profile_avatar.currentText())
            except (ValueError, PermissionError, OSError) as exc:
                self.info.setText("Profile not created: " + str(exc))
                return
            self.render()
            self.info.setText("Child profile created. It will appear on the login screen.")

        def save_activities(self):
            if not self.session or not self.profiles or not self.activity_checks: return
            try:
                ActivityPreferences(self.session, self.profiles).save(
                    self.state.child_id, {name: widget.isChecked() for name, widget in self.activity_checks.items()})
            except (PermissionError, ValueError, OSError) as exc:
                self.info.setText("Activity choices not saved: " + str(exc))
                return
            self.info.setText("Activity choices saved for this child.")

        def open_activity(self, activity):
            if self.state.page != "home" or not self.profiles or not self.session:
                return
            if self.profiles.get(self.state.child_id) is None:
                return
            if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get(activity, True):
                return
            if activity == "number-meadow":
                self.number_game = NumberMeadow()
                self.number_game.new_round()
                self.transition(NavigationState(page="number-meadow", child_id=self.state.child_id))
            elif activity == "word-woodland":
                self.word_game = WordWoodland()
                self.word_game.new_round()
                self.transition(NavigationState(page="word-woodland", child_id=self.state.child_id))
            elif activity == "puzzle-pond":
                self.puzzle_game = PuzzlePond()
                self.puzzle_waiting = False
                self.transition(NavigationState(page="puzzle-pond", child_id=self.state.child_id))
            elif activity == "nature-explorer":
                self.nature_game = NatureExplorer()
                self.transition(NavigationState(page=activity, child_id=self.state.child_id))
            elif activity == "feelings":
                self.feelings_game = FeelingsSpace()
                self.transition(NavigationState(page=activity, child_id=self.state.child_id))
            elif activity == "art-studio":
                self.art_game = ArtBoard()
                self.art_canvas = ArtCanvas()
                self.art_canvas.sticker_layer_changed.connect(self.sync_art_sticker_layers)
                self.art_canvas.sticker_collection_changed.connect(self.sync_art_sticker_collection)
                self.transition(NavigationState(page=activity, child_id=self.state.child_id))
            elif activity == "my-day":
                self.day_game = Routine(ROUTINES["full_day"])
                self.transition(NavigationState(page=activity, child_id=self.state.child_id))
            elif activity == "story-garden":
                self.story_game = StoryGarden()
                catalogue = Path(__file__).resolve().parent.parent / "assets" / "stories" / "75-books-staging.json"
                try:
                    data = json.loads(catalogue.read_text(encoding="utf-8"))
                    self.story_books = tuple(book for book in data["books"] if isinstance(book, dict) and isinstance(book.get("id"), str) and isinstance(book.get("title"), str) and isinstance(book.get("pages"), list) and book["pages"] and all(isinstance(page, dict) and isinstance(page.get("text"), str) for page in book["pages"]))
                except (OSError, ValueError, KeyError, TypeError):
                    self.story_books = ()
                self.story_selected = None
                self.story_page = 0
                self.transition(NavigationState(page=activity, child_id=self.state.child_id))
            else:
                self.info.setText("Activity integration pending")

        def open_my_artwork(self):
            if self.state.page != "home" or self.garden_stars_service() is None:
                return False
            self.artwork_preview = None
            self.transition(NavigationState(page="my-artwork", child_id=self.state.child_id))
            return True

        def select_artwork(self, filename):
            if self.state.page != "my-artwork" or not isinstance(filename, str):
                return False
            if not filename.startswith("eden-art-") or not filename.endswith(".png") or not filename[9:-4].isdigit():
                return False
            if self.garden_stars_service() is None:
                return False
            directory = self.profiles.path.parent / "art-studio" / self.state.child_id
            path = directory / filename
            if not path.is_file() or path.is_symlink():
                return False
            self.artwork_preview = filename
            self.render()
            return True

        def sticker_garden_path(self):
            if self.state.page != "sticker-garden" or self.garden_stars_service() is None:
                return None
            if not self.state.child_id.replace("_", "").replace("-", "").isalnum():
                return None
            return self.profiles.path.parent / "sticker-garden" / (self.state.child_id + ".json")

        def open_sticker_garden(self):
            if self.state.page != "home" or self.garden_stars_service() is None:
                return False
            self.garden_selected_sku = None
            self.garden_selected_slot = None
            self.garden_clear_confirm = False
            self.garden_category = "All"
            self.transition(NavigationState(page="sticker-garden", child_id=self.state.child_id))
            return True

        def select_garden_sticker(self, sku):
            if self.sticker_garden_path() is None or sku not in self.art_allowed_stickers_for_garden():
                return False
            self.garden_selected_sku = sku
            self.render()
            self.focus_garden_sticker(sku)
            return True

        def focus_garden_sticker(self, sku):
            if self.state.page != "sticker-garden":
                return
            for button in self.controls_widget.findChildren(QPushButton, "stickerGardenPicker"):
                if button.property("stickerSku") == sku and button.isVisible():
                    QTimer.singleShot(0, lambda target=button: target.setFocus(Qt.FocusReason.OtherFocusReason))
                    return

        def focus_garden_slot(self, slot):
            if self.state.page != "sticker-garden":
                return
            for button in self.controls_widget.findChildren(QPushButton, "stickerGardenSlot"):
                if button.property("gardenSlot") == slot and button.isVisible():
                    QTimer.singleShot(0, lambda target=button: target.setFocus(Qt.FocusReason.OtherFocusReason))
                    return

        def art_allowed_stickers_for_garden(self):
            service = self.garden_stars_service()
            if service is None:
                return set()
            root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
            catalogue = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["items"]
            owned = {item["sku"] for item in service.collection(self.state.child_id)}
            return {item["sku"] for item in catalogue if item["price"] == 0 or item["sku"] in owned}

        def place_garden_sticker(self, slot):
            path = self.sticker_garden_path()
            if path is None or type(slot) is not int or not 0 <= slot < SLOTS:
                return False
            allowed = self.art_allowed_stickers_for_garden()
            if self.garden_selected_sku not in allowed:
                return False
            placements = load_garden(path, allowed)
            placements[slot] = self.garden_selected_sku
            save_garden(path, placements, allowed)
            self.garden_selected_slot = slot
            self.garden_clear_confirm = False
            self.render()
            self.focus_garden_slot(slot)
            return True

        def select_garden_category(self, category):
            if self.sticker_garden_path() is None or category not in ("All", "Animals", "Nature", "Food", "Learning", "Things", "Places"):
                return False
            self.garden_category = category
            self.render()
            return True

        def place_next_garden_sticker(self):
            path = self.sticker_garden_path()
            if path is None:
                return False
            placements = load_garden(path, self.art_allowed_stickers_for_garden())
            return next((self.place_garden_sticker(slot) for slot in range(SLOTS) if slot not in placements), False)

        def select_garden_slot(self, slot):
            path = self.sticker_garden_path()
            if path is None or type(slot) is not int or not 0 <= slot < SLOTS:
                return False
            placements = load_garden(path, self.art_allowed_stickers_for_garden())
            if slot not in placements:
                return False
            self.garden_selected_slot = slot
            self.render()
            self.focus_garden_slot(slot)
            return True

        def move_garden_sticker(self, dx, dy):
            path = self.sticker_garden_path()
            slot = self.garden_selected_slot
            if path is None or type(slot) is not int or dx not in (-1, 0, 1) or dy not in (-1, 0, 1) or abs(dx) + abs(dy) != 1:
                return False
            row, col = divmod(slot, 6)
            next_row, next_col = row + dy, col + dx
            if not 0 <= next_row < 4 or not 0 <= next_col < 6:
                return False
            target = next_row * 6 + next_col
            allowed = self.art_allowed_stickers_for_garden()
            placements = load_garden(path, allowed)
            if slot not in placements or target in placements:
                return False
            placements[target] = placements.pop(slot)
            save_garden(path, placements, allowed)
            self.garden_selected_slot = target
            self.render()
            self.focus_garden_slot(target)
            return True

        def clear_sticker_garden(self):
            path = self.sticker_garden_path()
            if path is None:
                return False
            if not self.garden_clear_confirm:
                self.garden_clear_confirm = True
                self.render()
                return False
            save_garden(path, {}, self.art_allowed_stickers_for_garden())
            self.garden_clear_confirm = False
            self.garden_selected_slot = None
            self.render()
            return True

        def remove_garden_sticker(self, slot):
            path = self.sticker_garden_path()
            if path is None or type(slot) is not int or not 0 <= slot < SLOTS:
                return False
            allowed = self.art_allowed_stickers_for_garden()
            placements = load_garden(path, allowed)
            if slot not in placements:
                return False
            del placements[slot]
            save_garden(path, placements, allowed)
            self.garden_selected_slot = None
            self.garden_clear_confirm = False
            self.render()
            return True

        def garden_stars_service(self):
            if not self.profiles or not self.session or not self.state.child_id:
                return None
            if self.profiles.get(self.state.child_id) is None:
                return None
            service = GardenStars(self.profiles.path.parent / "garden-stars.sqlite3")
            service.create_profile(self.state.child_id)
            return service

        def parent_unlock_sticker(self):
            if self.state.page != "parent" or not self.state.parent_unlocked or self.parent_reward_combo is None:
                return False
            service = self.garden_stars_service()
            if service is None:
                return False
            sku = self.parent_reward_combo.currentData()
            if not isinstance(sku, str):
                return False
            try:
                result = service.unlock(self.state.child_id, sku, parent_authorized=True)
            except (OSError, ValueError):
                self.info.setText("Could not unlock this sticker")
                return False
            self.render()
            self.info.setText("Parent-unlocked sticker is ready in Art Studio" if result["source"] == "parent" else "Sticker already collected")
            return True

        def award_garden_stars(self, activity):
            service = self.garden_stars_service()
            if service is None:
                return 0
            try:
                result = service.earn(self.state.child_id, activity, str(uuid.uuid4()))
                return result.get("awarded", 0)
            except (OSError, ValueError):
                return 0

        def open_garden_stars(self):
            if self.state.page != "home" or self.garden_stars_service() is None:
                return False
            self.transition(NavigationState(page="garden-stars", child_id=self.state.child_id))
            return True

        def purchase_garden_sticker(self, sku):
            if self.state.page != "garden-stars":
                return False
            service = self.garden_stars_service()
            if service is None:
                return False
            try:
                # Parent-free unlocks must be handled separately after PIN verification.
                result = service.unlock(self.state.child_id, sku, parent_authorized=False)
            except (ValueError, OSError) as exc:
                self.info.setText("Sticker not unlocked: " + str(exc))
                return False
            self.render()
            self.info.setText("Sticker unlocked for Art Studio!" if result["spent"] else "Sticker already collected")
            return True

        def art_allowed_stickers(self):
            """Free stickers plus this child's earned/parent-unlocked rewards in isolated data."""
            if self.art_project_directory() is None:
                return set()
            root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
            manifest = json.loads((root / "manifest.json").read_text())
            valid = {entry["sku"] for entry in manifest["items"] if isinstance(entry.get("sku"), str)}
            free = {entry["sku"] for entry in manifest["items"] if entry.get("price") == 0}
            stars = GardenStars(self.profiles.path.parent / "garden-stars.sqlite3")
            stars.create_profile(self.state.child_id)
            owned = {entry["sku"] for entry in stars.collection(self.state.child_id)}
            return free | (owned & valid)

        def art_project_directory(self):
            if self.state.page != "art-studio" or self.art_canvas is None or self.art_game is None:
                return None
            if not self.profiles or not self.session or not self.state.child_id:
                return None
            if self.profiles.get(self.state.child_id) is None:
                return None
            if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get("art-studio", True):
                return None
            child = self.state.child_id
            if not child.replace("_", "").replace("-", "").isalnum():
                return None
            return self.profiles.path.parent / "art-studio" / child

        def add_art_sticker(self, sku, path):
            if self.art_project_directory() is None or sku not in self.art_allowed_stickers():
                return False
            if self.art_canvas is None or self.art_game is None or len(self.art_game.stamps) >= self.art_game.limit:
                return False
            if not self.art_canvas.add_sticker(path, sku):
                return False
            self.render()
            return True

        def sync_art_sticker_collection(self):
            if self.art_project_directory() is None or self.art_canvas is None or self.art_game is None:
                return
            allowed = self.art_allowed_stickers()
            skus = self.art_canvas.sticker_skus
            if any(sku not in allowed for sku in skus):
                return
            from .approved_models.art_studio_model import Stamp
            # Free emoji stamps are a separate layer; approved-sticker undo
            # must never silently erase them from the canonical ArtBoard.
            free_stamps = [stamp for stamp in self.art_game.stamps if stamp.symbol not in allowed]
            self.art_game.stamps[:] = free_stamps + [Stamp(sku, "approved") for sku in skus]
            self.render()

        def move_art_sticker_layer(self, direction):
            if self.art_project_directory() is None or self.art_canvas is None or self.art_game is None:
                return
            # Both toolbar and keyboard use the same signal-backed model sync.
            self.art_canvas.move_selected_sticker_layer(direction)

        def sync_art_sticker_layers(self):
            if self.art_project_directory() is None or self.art_canvas is None or self.art_game is None:
                return
            allowed = self.art_allowed_stickers()
            old = [stamp for stamp in self.art_game.stamps if stamp.symbol in allowed]
            new_order = self.art_canvas.sticker_skus
            if len(old) != len(new_order):
                return
            buckets = {}
            for stamp in old:
                buckets.setdefault(stamp.symbol, []).append(stamp)
            if any(sku not in buckets or not buckets[sku] for sku in new_order):
                return
            reordered = [buckets[sku].pop(0) for sku in new_order]
            iterator = iter(reordered)
            self.art_game.stamps[:] = [next(iterator) if stamp.symbol in allowed else stamp for stamp in self.art_game.stamps]
            self.render()

        def save_art_project(self):
            directory = self.art_project_directory()
            if directory is None: return
            try:
                # Persist only stickers permitted for the current child.
                root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
                manifest = json.loads((root / "manifest.json").read_text())
                allowed = self.art_allowed_stickers()
                skus = [stamp.symbol for stamp in self.art_game.stamps if stamp.symbol in allowed]
                self.art_canvas.save_project(directory, skus)
                self.info.setText("Editable drawing saved")
            except (OSError, ValueError, TypeError, KeyError):
                self.info.setText("Could not save editable drawing")

        def load_art_project(self):
            directory = self.art_project_directory()
            if directory is None: return
            try:
                root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
                manifest = json.loads((root / "manifest.json").read_text())
                allowed = self.art_allowed_stickers()
                skus = self.art_canvas.load_project(directory, allowed_stickers=allowed)
                self.art_game.clear()
                for sku in skus:
                    if sku in allowed:
                        self.art_game.add(sku, "approved")
                self.render()
                self.info.setText("Editable drawing restored")
            except (OSError, ValueError, TypeError, KeyError):
                self.info.setText("No valid saved drawing found")

        def save_art_picture(self):
            if self.state.page != "art-studio" or self.art_canvas is None or self.state.child_id is None:
                return
            if not self.profiles or self.profiles.get(self.state.child_id) is None:
                return
            if not self.session or not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get("art-studio", True):
                return
            safe_child = self.state.child_id
            if not safe_child.replace("_", "").replace("-", "").isalnum():
                return
            directory = self.profiles.path.parent / "art-studio" / safe_child
            try:
                saved = self.art_canvas.save_png(directory)
                self.award_garden_stars("art_studio")
                self.info.setText("Saved picture: " + saved.name)
            except OSError:
                self.info.setText("Could not save your picture")

        def stop_story_audio(self):
            if self.story_audio is not None:
                self.story_audio.stop()
                self.story_audio.setSource(QUrl())

        def play_story_audio(self):
            if self.state.page != "story-garden" or self.story_selected is None: return
            book = self.story_books[self.story_selected]
            audio = Path(__file__).resolve().parent.parent / "assets" / "stories" / "audio" / book["id"] / ("page-" + str(self.story_page + 1).zfill(2) + ".mp3")
            if QMediaPlayer is None or os.environ.get("QT_QPA_PLATFORM") == "offscreen":
                self.info.setText("Narration playback needs an audio-enabled desktop")
            elif audio.is_file() and not audio.is_symlink():
                if self.story_audio is None:
                    self.story_audio = QMediaPlayer(self)
                    self.story_output = QAudioOutput(self)
                    self.story_audio.setAudioOutput(self.story_output)
                    self.story_output.setVolume(0.75)
                self.stop_story_audio()
                self.story_audio.setSource(QUrl.fromLocalFile(str(audio)))
                self.story_audio.play()
            else:
                self.info.setText("Narration unavailable for this page")

        def select_story(self, index):
            if self.state.page != "story-garden" or not 0 <= index < len(self.story_books): return
            self.stop_story_audio()
            self.story_selected = index
            self.story_page = 0
            self.render()

        def change_story_page(self, delta):
            if self.state.page != "story-garden" or self.story_selected is None: return
            self.stop_story_audio()
            pages = self.story_books[self.story_selected]["pages"]
            self.story_page = max(0, min(len(pages)-1, self.story_page + delta))
            self.render()

        def back_to_story_shelf(self):
            if self.state.page != "story-garden": return
            self.stop_story_audio()
            self.story_selected = None
            self.story_page = 0
            self.render()

        def answer_word(self, value):
            if self.state.page != "word-woodland" or self.word_game is None: return
            if self.word_game.answer(value):
                self.award_garden_stars("word_woodland")
                self.word_game.new_round()
                self.render()
                self.info.setText("Well done! Let's try another word.")
            else:
                self.info.setText("Try another letter!")

        def choose_puzzle(self, index):
            if self.state.page != "puzzle-pond" or self.puzzle_game is None or self.puzzle_waiting: return
            result = self.puzzle_game.choose(index)
            if result == "second":
                self.puzzle_waiting = True
                game = self.puzzle_game
                child = self.state.child_id
                self.render()
                QTimer.singleShot(850, lambda: self.finish_puzzle_mismatch(game, child))
            else:
                self.render()
                if result == "matched":
                    if self.puzzle_game.complete:
                        self.award_garden_stars("puzzle_pond")
                    self.info.setText("Great match!" if not self.puzzle_game.complete else "All pairs found! Well done!")

        def finish_puzzle_mismatch(self, game, child):
            if self.state.page != "puzzle-pond" or self.state.child_id != child or self.puzzle_game is not game:
                return
            game.finish_mismatch()
            self.puzzle_waiting = False
            self.render()
            self.info.setText("Not a match. Try again!")

        def answer_number(self, value):
            if self.state.page != "number-meadow" or self.number_game is None:
                return
            if self.number_game.answer(value):
                self.award_garden_stars("number_meadow")
                self.number_game.new_round()
                self.render()
                self.info.setText("Well done! Here's another number.")
            else:
                self.info.setText("Try again — you can do it!")

        def render(self):
            # Qt may emit a stale category-change signal while deleting the
            # previous picker; never let it reset the current filter.
            old_category_picker = self.controls_widget.findChild(QComboBox, "stickerGardenCategory")
            if old_category_picker is not None:
                old_category_picker.blockSignals(True)
            while self.buttons.count():
                item = self.buttons.takeAt(0)
                if item.widget():
                    item.widget().hide()
                    item.widget().deleteLater()
            self.pin_input = None
            self.pin_confirm = None
            self.profile_name = None
            self.profile_username = None
            self.profile_avatar = None
            self.activity_checks = {}
            self.parent_reward_combo = None
            self.activity_grid = None
            self.avatar_image.clear()
            self.avatar_image.hide()
            activity_titles = {"number-meadow": "Number Meadow", "word-woodland": "Word Woodland",
                               "puzzle-pond": "Puzzle Pond", "art-studio": "Art Studio",
                               "nature-explorer": "Nature Explorer", "my-day": "My Day",
                               "feelings": "Feelings", "story-garden": "Story Garden"}
            is_activity = self.state.page in activity_titles
            self.activity_toolbar.setVisible(is_activity)
            self.title.setVisible(not is_activity)
            if is_activity:
                self.toolbar_heading.setText(activity_titles[self.state.page])
                self.toolbar_heading.setAccessibleName(activity_titles[self.state.page])
            self.info.setText("Native preview · " + self.state.page + " · " + detect_platform().name)
            def action(label, callback, grid=None, index=None):
                button = QPushButton(label)
                button.setMinimumHeight(56)
                button.setAccessibleName(label)
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.clicked.connect(lambda _checked=False: callback())
                if grid is None:
                    self.buttons.addWidget(button)
                else:
                    grid.addWidget(button, index // 4, index % 4)
            if self.state.page == "login":
                if self.profiles is not None:
                    cards = self.profiles.all()
                    if not cards:
                        self.info.setText("Welcome to Eden — ask a parent to set up the first child")
                        if self.pin_adapter:
                            action("Parent setup", lambda: self.transition(self.state.open_parent()))
                    for card in cards:
                        action(card.display_name, lambda username=card.username: self.transition(self.state.select_child(username)))
                else:
                    action("Preview child session", lambda: self.transition(self.state.select_child("demo-only")))
            elif self.state.page in ("my-day", "story-garden"):
                activity = self.state.page
                game = self.day_game if activity == "my-day" else self.story_game
                if not self.profiles or not self.session or self.profiles.get(self.state.child_id) is None or game is None:
                    self.transition(self.state.logout())
                    return
                if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get(activity, True):
                    self.transition(NavigationState(page="home", child_id=self.state.child_id))
                    return
                if activity == "my-day":
                    self.info.setText("My Day — tick the things you've done")
                    grid_widget = QWidget()
                    grid = QGridLayout(grid_widget)
                    for index, step in enumerate(game.steps):
                        label = ("✓ " if game.completed[index] else "○ ") + step.symbol + " " + step.label
                        action(label, lambda i=index: (game.toggle(i), self.render()), grid, index)
                    self.buttons.addWidget(grid_widget)
                    if game.finished:
                        self.buttons.addWidget(QLabel("All done — wonderful!"))
                    action("Start again", lambda: (game.reset(), self.render()))
                else:
                    self.info.setText("Story Garden — choose a book")
                    if self.story_books and self.story_selected is None:
                        grid_widget = QWidget()
                        grid = QGridLayout(grid_widget)
                        for index, book in enumerate(self.story_books):
                            action(book["title"] + (" (draft)" if book.get("status") == "text-draft" else ""), lambda i=index: self.select_story(i), grid, index)
                        self.buttons.addWidget(grid_widget)
                    elif self.story_books and self.story_selected is not None:
                        book = self.story_books[self.story_selected]
                        page = book["pages"][self.story_page]
                        self.info.setText(book["title"] + (" — draft, not approved" if book.get("status") == "text-draft" else ""))
                        picture_file = (Path(__file__).resolve().parent.parent / "assets" / "stories" / "artwork-staging" / book["id"] / ("page-" + str(self.story_page + 1).zfill(2) + ".png"))
                        if picture_file.is_file() and not picture_file.is_symlink():
                            pixmap = QPixmap(str(picture_file))
                            if not pixmap.isNull():
                                illustration = QLabel()
                                illustration.setObjectName("storyPageIllustration")
                                illustration.setAccessibleName("Staging illustration for " + book["title"])
                                illustration.setPixmap(pixmap.scaled(500, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                                illustration.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.buttons.addWidget(illustration)
                        story_text = QLabel(page["text"])
                        story_text.setWordWrap(True)
                        story_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        story_text.setAccessibleName("Story page " + str(self.story_page + 1))
                        self.buttons.addWidget(story_text)
                        self.buttons.addWidget(QLabel("Page " + str(self.story_page + 1) + " of " + str(len(book["pages"]))))
                        action("Listen to page", self.play_story_audio)
                        action("Stop narration", self.stop_story_audio)
                        if self.story_page > 0:
                            action("Previous page", lambda: self.change_story_page(-1))
                        if self.story_page < len(book["pages"]) - 1:
                            action("Next page", lambda: self.change_story_page(1))
                        else:
                            action("Read again", lambda: self.select_story(self.story_selected))
                        action("Choose another book", self.back_to_story_shelf)
                    else:
                        self.info.setText("Story Garden — sample story (catalogue unavailable)")
                        scene = game.scene
                        picture = QLabel(scene.symbol)
                        picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.buttons.addWidget(picture)
                        story_text = QLabel(scene.sentence)
                        story_text.setWordWrap(True)
                        self.buttons.addWidget(story_text)
                        if game.finished:
                            action("Read again", lambda: (game.restart(), self.render()))
                        else:
                            action("Next page", lambda: (game.next_scene(), self.render()))
                action("Back to home", lambda: (self.stop_story_audio(), self.transition(NavigationState(page="home", child_id=self.state.child_id))))
                action("Log out", lambda: (self.stop_story_audio(), self.transition(self.state.logout())))
            elif self.state.page == "art-studio":
                game = self.art_game
                if not self.profiles or not self.session or self.profiles.get(self.state.child_id) is None or game is None:
                    self.transition(self.state.logout())
                    return
                if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get("art-studio", True):
                    self.transition(NavigationState(page="home", child_id=self.state.child_id))
                    return
                self.info.setText("Pick a wallpaper, add stickers, or draw!")
                if self.art_canvas is not None:
                    self.art_canvas.setParent(None)
                    # Mirror the approved iMac's arrangement: a horizontal
                    # action strip, 220px tool sidebar and large drawing area.
                    studio = QWidget()
                    studio.setObjectName("edenArtStudioScene")
                    # Approved live iMac art-studio-refresh.css palette; scoped
                    # to this scene to avoid changing other activities.
                    studio.setStyleSheet("""
                        QWidget#edenArtStudioScene { background: #f8f4df; }
                        QScrollArea#edenArtStudioSidebar {
                            background: #f9f5d9; border: 4px solid #85aa80;
                            border-radius: 23px; }
                        QWidget#edenArtStudioSidebarContent { background: #f9f5d9; }
                        QLabel#edenArtStudioBrushHeading,
                        QLabel#edenArtStudioColourHeading,
                        QLabel#edenArtStudioWallpaperHeading {
                            color: #245e47; font-size: 24px; font-weight: 900; }
                        QWidget#edenArtStudioActions QPushButton,
                        QWidget#edenArtStudioDock QPushButton {
                            min-height: 48px; font-size: 18px; font-weight: 800; }
                        QWidget#edenArtStudioWorkspace QWidget#artStudioDrawingCanvas {
                            border: 5px solid #b991cf; border-radius: 23px; }
                    """)
                    studio_layout = QVBoxLayout(studio)
                    studio_layout.setSpacing(8)
                    topbar = QWidget()
                    topbar.setObjectName("edenArtStudioActions")
                    top_actions = QHBoxLayout(topbar)
                    top_actions.setContentsMargins(0, 0, 0, 0)
                    def studio_button(label, callback, target):
                        button = QPushButton(label)
                        button.setAccessibleName(label)
                        button.setMinimumHeight(48)
                        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                        button.clicked.connect(lambda _checked=False: callback())
                        target.addWidget(button)
                        return button
                    for label, callback in (
                        ("Draw", lambda: self.art_canvas.set_eraser(False)),
                        ("Undo drawing", self.art_canvas.undo),
                        ("Redo drawing", self.art_canvas.redo),
                        ("Undo last action", self.art_canvas.undo_action),
                        ("Redo last action", self.art_canvas.redo_action),
                        ("Save", self.save_art_picture),
                        ("Clear drawing", self.art_canvas.clear),
                    ):
                        studio_button(label, callback, top_actions)
                    studio_layout.addWidget(topbar)
                    workspace = QWidget()
                    workspace.setObjectName("edenArtStudioWorkspace")
                    work_layout = QHBoxLayout(workspace)
                    work_layout.setContentsMargins(0, 0, 0, 0)
                    sidebar_scroll = QScrollArea()
                    sidebar_scroll.setObjectName("edenArtStudioSidebar")
                    sidebar_scroll.setWidgetResizable(True)
                    sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    sidebar_scroll.setFixedWidth(220)
                    sidebar = QWidget()
                    sidebar.setObjectName("edenArtStudioSidebarContent")
                    sidebar_layout = QVBoxLayout(sidebar)
                    sidebar_layout.setSpacing(7)
                    brush_label = QLabel("✏️ Brushes")
                    brush_label.setObjectName("edenArtStudioBrushHeading")
                    sidebar_layout.addWidget(brush_label)
                    brush_grid_widget = QWidget()
                    brush_grid = QGridLayout(brush_grid_widget)
                    for index, (name, width) in enumerate((("Pen", 3), ("Pencil", 4), ("Crayon", 13), ("Paint", 20))):
                        brush_button = QPushButton(name)
                        brush_button.setAccessibleName(name + " brush")
                        brush_button.setMinimumHeight(58)
                        brush_button.clicked.connect(lambda _checked=False, w=width: self.art_canvas.set_brush_width(w))
                        brush_grid.addWidget(brush_button, index // 2, index % 2)
                    sidebar_layout.addWidget(brush_grid_widget)
                    studio_button("Eraser", lambda: self.art_canvas.set_eraser(True), sidebar_layout)
                    for label, width in (("Small brush", 3), ("Medium brush", 6), ("Large brush", 12)):
                        studio_button(label, lambda w=width: self.art_canvas.set_brush_width(w), sidebar_layout)
                    colour_label = QLabel("🎨 Colours")
                    colour_label.setObjectName("edenArtStudioColourHeading")
                    sidebar_layout.addWidget(colour_label)
                    colour_grid_widget = QWidget()
                    colour_grid = QGridLayout(colour_grid_widget)
                    for index, colour in enumerate(PALETTE):
                        button = QPushButton(colour)
                        button.setAccessibleName(colour + " paint")
                        button.setMinimumHeight(48)
                        button.clicked.connect(lambda _checked=False, c=colour: self.art_canvas.set_colour(c))
                        colour_grid.addWidget(button, index // 3, index % 3)
                    sidebar_layout.addWidget(colour_grid_widget)
                    wallpaper_label = QLabel("🌄 Wallpapers")
                    wallpaper_label.setObjectName("edenArtStudioWallpaperHeading")
                    sidebar_layout.addWidget(wallpaper_label)
                    wallpaper_grid_widget = QWidget()
                    wallpaper_grid_widget.setObjectName("edenArtStudioWallpaperPicker")
                    wallpaper_grid = QGridLayout(wallpaper_grid_widget)
                    for index, background in enumerate(BACKGROUNDS):
                        button = QPushButton(background)
                        button.setAccessibleName(background + " background")
                        button.setMinimumHeight(48)
                        button.clicked.connect(lambda _checked=False, name=background: self.art_canvas.set_background(name))
                        wallpaper_grid.addWidget(button, index // 2, index % 2)
                    sidebar_layout.addWidget(wallpaper_grid_widget)
                    sidebar_layout.addStretch(1)
                    sidebar_scroll.setWidget(sidebar)
                    work_layout.addWidget(sidebar_scroll)
                    self.art_canvas.setMinimumSize(440, 260)
                    self.art_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    work_layout.addWidget(self.art_canvas, 1)
                    studio_layout.addWidget(workspace, 1)
                    dock = QWidget()
                    dock.setObjectName("edenArtStudioDock")
                    dock_layout = QHBoxLayout(dock)
                    dock_layout.setContentsMargins(0, 0, 0, 0)
                    for label, callback in (
                        ("Undo sticker move", self.art_canvas.undo_sticker_move),
                        ("Redo sticker move", self.art_canvas.redo_sticker_move),
                        ("Remove selected sticker", self.art_canvas.remove_selected_sticker),
                        ("Sticker back", lambda: self.move_art_sticker_layer(-1)),
                        ("Sticker forward", lambda: self.move_art_sticker_layer(1)),
                        ("Save picture", self.save_art_picture),
                        ("Save editable drawing", self.save_art_project),
                        ("Open saved drawing", self.load_art_project),
                    ):
                        studio_button(label, callback, dock_layout)
                    studio_layout.addWidget(dock)
                    self.buttons.addWidget(studio)
                sticker_root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
                sticker_map = {}
                try:
                    sticker_manifest = json.loads((sticker_root / "manifest.json").read_text())
                    allowed_stickers = self.art_allowed_stickers()
                    for entry in sticker_manifest.get("items", []):
                        if entry.get("sku") in allowed_stickers and isinstance(entry.get("sku"), str) and isinstance(entry.get("filename"), str):
                            candidate = sticker_root / entry["filename"]
                            if candidate.is_file() and not candidate.is_symlink() and candidate.parent == sticker_root:
                                sticker_map[entry["sku"]] = (entry["name"], candidate)
                except (OSError, ValueError, TypeError):
                    pass
                if self.art_canvas is not None:
                    selected_skus = [stamp.symbol for stamp in game.stamps if stamp.symbol in sticker_map]
                    if selected_skus != self.art_canvas.sticker_skus:
                        self.art_canvas.set_stickers([sticker_map[sku][1] for sku in selected_skus], selected_skus)
                picture = QLabel(" ".join(stamp.symbol for stamp in game.stamps if stamp.symbol not in sticker_map) or "Choose a sticker to begin")
                picture.setObjectName("artStudioCanvas")
                picture.setWordWrap(True)
                picture.setMinimumHeight(90)
                picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
                picture.setStyleSheet("font-size: 30px;")
                self.buttons.addWidget(picture)
                grid_widget = QWidget()
                grid = QGridLayout(grid_widget)
                for index, (symbol, colour) in enumerate((("🌼", "yellow"), ("🦋", "blue"), ("🌳", "green"), ("🐝", "yellow"))):
                    action("Add " + symbol, lambda sym=symbol, col=colour: (game.add(sym, col), self.render()), grid, index)
                self.buttons.addWidget(grid_widget)
                free_widget = QWidget()
                free_grid = QGridLayout(free_widget)
                for index, (sku, (name, path)) in enumerate(sticker_map.items()):
                    action("Sticker: " + name, lambda item=sku, image=path: self.add_art_sticker(item, image), free_grid, index)
                self.buttons.addWidget(free_widget)
                action("Undo", self.art_canvas.undo_action)
                action("Redo", self.art_canvas.redo_action)
                action("Clear", lambda: (game.clear(), self.art_canvas.set_stickers([], []), self.render()))
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page in ("nature-explorer", "feelings"):
                activity = self.state.page
                game = self.nature_game if activity == "nature-explorer" else self.feelings_game
                if not self.profiles or not self.session or self.profiles.get(self.state.child_id) is None or game is None:
                    self.transition(self.state.logout())
                    return
                if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get(activity, True):
                    self.transition(NavigationState(page="home", child_id=self.state.child_id))
                    return
                if activity == "nature-explorer":
                    item = game.current
                    self.info.setText("Nature Explorer — " + str(game.found_count) + " found")
                    art = picture_path("word-woodland", item.label)
                    picture = QLabel(item.symbol + "  " + item.label)
                    picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    picture.setAccessibleName(item.label)
                    picture.setStyleSheet("font-size: 28px;")
                    if art:
                        pixmap = QPixmap(str(art))
                        if not pixmap.isNull():
                            picture.setPixmap(pixmap.scaled(140, 125, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    self.buttons.addWidget(picture)
                    hint = QLabel(item.hint)
                    hint.setWordWrap(True)
                    hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.buttons.addWidget(hint)
                    action("I found it!" if not game.is_found else "Found ✓", lambda: (game.mark_found(), self.render()))
                    action("Previous", lambda: (game.previous(), self.render()))
                    action("Next", lambda: (game.next(), self.render()))
                else:
                    self.info.setText("Feelings — how are you feeling today?")
                    grid_widget = QWidget()
                    grid = QGridLayout(grid_widget)
                    for index, feeling in enumerate(FEELINGS):
                        action(feeling.symbol + " " + feeling.label, lambda key=feeling.key: (game.choose_mood(key), self.render()), grid, index)
                    self.buttons.addWidget(grid_widget)
                    if game.mood:
                        mood_label = QLabel("You chose: " + game.mood.label + ". You can take your time.")
                        mood_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.buttons.addWidget(mood_label)
                    for index, (symbol, instruction) in enumerate(CALM_ACTIONS):
                        action(("✓ " if game.completed[index] else "○ ") + symbol + " " + instruction, lambda i=index: (game.toggle_action(i), self.render()))
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page in ("word-woodland", "puzzle-pond"):
                activity = self.state.page
                game = self.word_game if activity == "word-woodland" else self.puzzle_game
                if not self.profiles or not self.session or self.profiles.get(self.state.child_id) is None or game is None:
                    self.transition(self.state.logout())
                    return
                if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get(activity, True):
                    self.transition(NavigationState(page="home", child_id=self.state.child_id))
                    return
                self.info.setText("Word Woodland — choose the first letter" if activity == "word-woodland" else "Puzzle Pond — find the matching pairs")
                if activity == "word-woodland":
                    round_ = game.round
                    picture = QLabel(round_.symbol + "  " + round_.word)
                    picture.setObjectName("wordWoodlandPrompt")
                    picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    picture.setStyleSheet("font-size: 30px;")
                    art = picture_path("word-woodland", round_.word)
                    if art:
                        pixmap = QPixmap(str(art))
                        if not pixmap.isNull():
                            picture.setPixmap(pixmap.scaled(140, 125, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            picture.setAccessibleName(round_.word)
                    self.buttons.addWidget(picture)
                    grid_widget = QWidget()
                    grid = QGridLayout(grid_widget)
                    for index, letter in enumerate(round_.choices):
                        action(letter, lambda value=letter: self.answer_word(value), grid, index)
                    self.buttons.addWidget(grid_widget)
                else:
                    grid_widget = QWidget()
                    grid = QGridLayout(grid_widget)
                    for card in game.cards:
                        label = card.symbol if card.revealed or card.matched else "?"
                        action(label, lambda index=card.index: self.choose_puzzle(index), grid, card.index)
                        button = grid.itemAtPosition(card.index // 4, card.index % 4).widget()
                        if card.revealed or card.matched:
                            art = picture_path("word-woodland", card.symbol)
                            if art is None and card.symbol == "Eden":
                                art = resolve_avatar("approved-eden")
                            if art and not QPixmap(str(art)).isNull():
                                button.setIcon(QIcon(str(art)))
                                button.setIconSize(QSize(52, 52))
                                button.setText("")
                                button.setAccessibleName(card.symbol)
                    self.buttons.addWidget(grid_widget)
                    if game.complete:
                        action("Play again", lambda: (game.restart(), self.render()))
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page == "number-meadow":
                if not self.profiles or not self.session or self.profiles.get(self.state.child_id) is None or self.number_game is None:
                    self.transition(self.state.logout())
                    return
                if not ActivityPreferences(self.session, self.profiles).load(self.state.child_id).get("number-meadow", True):
                    self.transition(NavigationState(page="home", child_id=self.state.child_id))
                    return
                round_ = self.number_game.round
                self.info.setText("Number Meadow — how many can you count?")
                art = picture_path("number-meadow", "bee")
                if art and not QPixmap(str(art)).isNull():
                    pictures_widget = QWidget()
                    pictures_widget.setObjectName("numberMeadowObjects")
                    pictures_grid = QGridLayout(pictures_widget)
                    pictures_grid.setSpacing(3)
                    pixmap = QPixmap(str(art)).scaled(56, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    for index in range(round_.count):
                        item = QLabel()
                        item.setPixmap(pixmap)
                        item.setAccessibleName("Bee " + str(index + 1))
                        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        pictures_grid.addWidget(item, index // 5, index % 5)
                    self.buttons.addWidget(pictures_widget)
                else:
                    picture = QLabel("🌼 " * round_.count)
                    picture.setObjectName("numberMeadowObjects")
                    picture.setWordWrap(True)
                    picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    picture.setStyleSheet("font-size: 23px;")
                    self.buttons.addWidget(picture)
                choices_widget = QWidget()
                choices_grid = QGridLayout(choices_widget)
                for index, number in enumerate(round_.choices):
                    action(str(number), lambda value=number: self.answer_number(value), choices_grid, index)
                self.buttons.addWidget(choices_widget)
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page == "my-artwork":
                if self.garden_stars_service() is None:
                    self.transition(self.state.logout())
                    return
                self.info.setText("My saved pictures")
                directory = self.profiles.path.parent / "art-studio" / self.state.child_id
                pictures = sorted((path for path in directory.glob("eden-art-*.png")
                                   if path.is_file() and not path.is_symlink()
                                   and path.stem[9:].isdigit()), key=lambda path: path.name, reverse=True) if directory.is_dir() else []
                if self.artwork_preview is not None:
                    selected = next((path for path in pictures if path.name == self.artwork_preview), None)
                    if selected is not None:
                        pixmap = QPixmap(str(selected))
                        if not pixmap.isNull():
                            preview = QLabel()
                            preview.setAccessibleName("Saved picture " + selected.name)
                            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            preview.setPixmap(pixmap.scaled(700, 450, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            self.buttons.addWidget(preview)
                if not pictures:
                    self.buttons.addWidget(QLabel("No pictures saved yet. Visit Art Studio to make one!"))
                for path in pictures[:100]:
                    action(path.name, lambda name=path.name: self.select_artwork(name))
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page == "sticker-garden":
                path = self.sticker_garden_path()
                if path is None:
                    self.transition(self.state.logout())
                    return
                allowed = self.art_allowed_stickers_for_garden()
                placements = load_garden(path, allowed)
                self.info.setText("My Sticker Garden — choose a sticker, then choose a place")
                root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
                catalogue = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["items"]
                names = {entry["sku"]: entry["name"] for entry in catalogue}
                filenames = {entry["sku"]: entry["filename"] for entry in catalogue}
                # Match the original iMac composition: narrow sticker picker on
                # the left, 6x4 placement board in the centre, actions on right.
                layout_widget = QWidget()
                layout_widget.setObjectName("stickerGardenThreePanel")
                compact_garden = self.width() < 1000
                panel_layout = QVBoxLayout(layout_widget) if compact_garden else QHBoxLayout(layout_widget)
                panel_layout.setSpacing(9)
                layout_widget.setStyleSheet("""
                    QWidget#stickerGardenPickerPanel, QWidget#stickerGardenActionsPanel {
                        background: #fff5e2; border: 4px solid white; border-radius: 19px;
                    }
                    QLabel#stickerGardenPanelHeading {
                        color: white; background: #196fc1; font-size: 18px;
                        font-weight: 900; border-radius: 14px; padding: 6px;
                    }
                    QPushButton#stickerGardenPicker {
                        background: white; border: 3px solid #cbd8e7;
                        border-radius: 16px; padding: 5px;
                    }
                    QPushButton#stickerGardenPicker[selected="true"] {
                        background: #eaffd9; border: 4px solid #4eaf42;
                    }
                    QPushButton#stickerGardenAction {
                        background: #166fbd; color: white; border: 3px solid white;
                        border-radius: 17px; font-weight: 900; font-size: 16px;
                    }
                    QPushButton#stickerGardenAction[role="clear"] { background: #d88412; }
                    QPushButton#stickerGardenAction[role="remove"] { background: #be272c; }
                    QPushButton#stickerGardenAction[role="place"] { background: #299e3e; }
                    QLabel#stickerGardenHelp {
                        background: #ffffffe7; color: #202639; border-radius: 12px;
                        padding: 5px; font-weight: 700;
                    }
                """)

                left_panel = QWidget()
                left_panel.setObjectName("stickerGardenPickerPanel")
                left_panel.setFixedWidth(212) if not compact_garden else left_panel.setMinimumWidth(0)
                left_layout = QVBoxLayout(left_panel)
                left_heading = QLabel("My Stickers")
                left_heading.setObjectName("stickerGardenPanelHeading")
                left_layout.addWidget(left_heading)
                categories = ("All", "Animals", "Nature", "Food", "Learning", "Things", "Places")
                category_picker = QComboBox()
                category_picker.setObjectName("stickerGardenCategory")
                category_picker.setAccessibleName("Sticker category")
                category_picker.addItems(categories)
                category_picker.setCurrentText(self.garden_category)
                category_picker.currentTextChanged.connect(self.select_garden_category)
                left_layout.addWidget(category_picker)
                picker_scroll = QScrollArea()
                picker_scroll.setObjectName("stickerGardenPickerScroll")
                picker_scroll.setWidgetResizable(True)
                picker_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                sticker_picker = QWidget()
                picker_grid = QGridLayout(sticker_picker)
                available = [item for item in catalogue if item["sku"] in allowed and
                             (self.garden_category == "All" or item["category"] == self.garden_category)]
                for index, entry in enumerate(available):
                    sku = entry["sku"]
                    button = QPushButton(entry["name"])
                    button.setObjectName("stickerGardenPicker")
                    button.setProperty("selected", sku == self.garden_selected_sku)
                    button.setProperty("stickerSku", sku)
                    button.setAccessibleName("Select " + entry["name"])
                    button.setAccessibleDescription("Selected sticker" if sku == self.garden_selected_sku else "Choose this sticker")
                    button.setMinimumHeight(78)
                    button.setIconSize(QSize(41, 41))
                    image = root / entry["filename"]
                    if image.is_file() and not image.is_symlink():
                        button.setIcon(QIcon(str(image)))
                    button.clicked.connect(lambda _checked=False, item=sku: self.select_garden_sticker(item))
                    picker_grid.addWidget(button, index // 2, index % 2)
                picker_scroll.setWidget(sticker_picker)
                left_layout.addWidget(picker_scroll, 1)
                if compact_garden:
                    picker_scroll.setFixedHeight(180)
                panel_layout.addWidget(left_panel)

                middle_panel = QWidget()
                middle_panel.setObjectName("stickerGardenCentrePanel")
                middle_layout = QVBoxLayout(middle_panel)
                board = QWidget()
                board.setObjectName("stickerGardenBoard")
                # Original iMac artwork board is 810px wide: avoid stretching
                # the 1672x941 approved image across a 1452px-wide desktop.
                board.setMaximumWidth(810)
                board.setMinimumSize(480 if compact_garden else 0, 310 if compact_garden else min(550, max(350, self.height() - 350)))
                # Use the exact approved 1672x941 original iMac background.
                # Never substitute unapproved artwork if it is missing.
                garden_background = Path(__file__).resolve().parent.parent / "assets" / "garden-stars" / "backgrounds" / "garden-background-v58.webp"
                if garden_background.is_file() and not garden_background.is_symlink() and not QPixmap(str(garden_background)).isNull():
                    board.setStyleSheet('QWidget#stickerGardenBoard { border-image: url("' + str(garden_background) + '") 0 0 0 0 stretch stretch; }')
                    board.setProperty("approvedGardenBackground", str(garden_background))
                board_grid = QGridLayout(board)
                board_grid.setSpacing(4)
                for slot in range(SLOTS):
                    sku = placements.get(slot)
                    row, column = divmod(slot, 6)
                    label = "Garden row " + str(row + 1) + " column " + str(column + 1) + (": " + names[sku] if sku else ": empty")
                    button = QPushButton("" if sku else "+")
                    button.setObjectName("stickerGardenSlot")
                    button.setProperty("gardenSlot", slot)
                    button.setAccessibleName(label)
                    button.setAccessibleDescription("Press Enter to select this sticker for moving or removing" if sku else "Choose a sticker first, then press Enter to place it")
                    button.setToolTip(label)
                    button.setMinimumHeight(64)
                    button.setIconSize(QSize(48, 48))
                    button.setStyleSheet("QPushButton { border: 0; background: transparent; font-size: 26px; font-weight: bold; } QPushButton:focus { border: 3px solid #f1c40f; }")
                    if sku:
                        image = root / filenames[sku]
                        if image.is_file() and not image.is_symlink():
                            button.setIcon(QIcon(str(image)))
                    button.clicked.connect(lambda _checked=False, position=slot, occupied=bool(sku): self.select_garden_slot(position) if occupied else self.place_garden_sticker(position))
                    board_grid.addWidget(button, row, column)
                middle_layout.addWidget(board, 1)
                help_text = QLabel("Choose a sticker, then tap a garden square.")
                help_text.setObjectName("stickerGardenHelp")
                middle_layout.addWidget(help_text)
                panel_layout.addWidget(middle_panel, 1)

                right_panel = QWidget()
                right_panel.setObjectName("stickerGardenActionsPanel")
                right_panel.setFixedWidth(160) if not compact_garden else right_panel.setMinimumWidth(0)
                right_layout = QVBoxLayout(right_panel)
                right_heading = QLabel("Move Sticker")
                right_heading.setObjectName("stickerGardenPanelHeading")
                right_layout.addWidget(right_heading)
                move_widget = QWidget()
                move_grid = QGridLayout(move_widget)
                for index, (label, dx, dy) in enumerate((("↑", 0, -1), ("←", -1, 0), ("→", 1, 0), ("↓", 0, 1))):
                    move_button = QPushButton(label)
                    move_button.setObjectName("stickerGardenAction")
                    move_button.setAccessibleName({"↑": "Move sticker up", "←": "Move sticker left", "→": "Move sticker right", "↓": "Move sticker down"}[label])
                    move_button.setMinimumHeight(52)
                    move_button.clicked.connect(lambda _checked=False, x=dx, y=dy: self.move_garden_sticker(x, y))
                    move_grid.addWidget(move_button, index // 2, index % 2)
                right_layout.addWidget(move_widget)
                if self.garden_selected_sku:
                    right_layout.addWidget(QLabel("Selected: " + names.get(self.garden_selected_sku, "Sticker")))
                def right_action(label, callback):
                    button = QPushButton(label)
                    button.setObjectName("stickerGardenAction")
                    button.setProperty("role", "clear" if label.startswith("Clear") else "remove" if label.startswith("Remove") else "place")
                    button.setAccessibleName(label)
                    button.setMinimumHeight(52)
                    button.clicked.connect(lambda _checked=False: callback())
                    right_layout.addWidget(button)
                if self.garden_selected_slot is not None and self.garden_selected_slot in placements:
                    right_action("Remove selected", lambda: self.remove_garden_sticker(self.garden_selected_slot))
                right_action("Place Sticker", self.place_next_garden_sticker)
                right_action("Clear Garden — confirm" if self.garden_clear_confirm else "Clear Garden", self.clear_sticker_garden)
                right_layout.addStretch(1)
                panel_layout.addWidget(right_panel)
                self.buttons.addWidget(layout_widget)
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page == "garden-stars":
                service = self.garden_stars_service()
                if service is None:
                    self.transition(self.state.logout())
                    return
                balance = service.balance(self.state.child_id)
                owned = {item["sku"] for item in service.collection(self.state.child_id)}
                self.info.setText("My Garden Stars — " + str(balance) + " stars")
                self.buttons.addWidget(QLabel("Choose a sticker to unlock with your earned stars. Collected stickers appear in Art Studio."))
                root = Path(__file__).resolve().parent.parent / "assets" / "stickers"
                catalogue = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["items"]
                sticker_grid_widget = QWidget()
                sticker_grid = QGridLayout(sticker_grid_widget)
                for index, entry in enumerate(catalogue):
                    sku, name, price = entry["sku"], entry["name"], entry["price"]
                    collected = sku in owned or price == 0
                    label = name + (" — Collected ✓" if collected else " — " + str(price) + " stars")
                    tile = QPushButton(label)
                    tile.setObjectName("gardenStarsStickerTile")
                    tile.setAccessibleName(label)
                    tile.setAccessibleDescription("Already collected" if collected else "Unlock for " + str(price) + " Garden Stars")
                    tile.setMinimumHeight(100)
                    tile.setIconSize(QSize(76, 76))
                    filename = entry.get("filename", "")
                    if isinstance(filename, str) and filename.startswith("sticker_") and filename.endswith(".png") and "/" not in filename and "\\" not in filename:
                        image = root / filename
                        if image.is_file() and not image.is_symlink():
                            tile.setIcon(QIcon(str(image)))
                    tile.clicked.connect(lambda _checked=False, item=sku: self.purchase_garden_sticker(item))
                    sticker_grid.addWidget(tile, index // 4, index % 4)
                self.buttons.addWidget(sticker_grid_widget)
                action("Back to home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            elif self.state.page == "home":
                if self.profiles is not None:
                    card = self.profiles.get(self.state.child_id)
                    if card is None:
                        self.transition(self.state.logout())
                        return
                    self.info.setText("Welcome, " + card.display_name)
                    path = resolve_avatar(card.avatar)
                    if path:
                        pixmap = QPixmap(str(path))
                        if not pixmap.isNull():
                            self.avatar_image.setPixmap(pixmap.scaled(110, 115, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            self.avatar_image.show()
                if self.profiles is not None and self.session is not None:
                    enabled = ActivityPreferences(self.session, self.profiles).load(self.state.child_id)
                    grid_widget = QWidget()
                    self.activity_grid = QGridLayout(grid_widget)
                    self.activity_grid.setSpacing(8)
                    position = 0
                    for activity in ACTIVITIES:
                        if enabled.get(activity, True):
                            action(activity.replace("-", " ").title(), lambda name=activity: self.open_activity(name), self.activity_grid, position)
                            position += 1
                    self.buttons.addWidget(grid_widget)
                extras_widget = QWidget()
                extras_grid = QGridLayout(extras_widget)
                action("My Garden Stars", self.open_garden_stars, extras_grid, 0)
                action("My saved pictures", self.open_my_artwork, extras_grid, 1)
                action("My Sticker Garden", self.open_sticker_garden, extras_grid, 2)
                self.buttons.addWidget(extras_widget)
                action("Parent Corner", lambda: self.transition(self.state.open_parent()))
                action("Log out", lambda: self.transition(self.state.logout()))
            else:
                if self.state.parent_unlocked:
                    self.info.setText("Parent Corner unlocked — child profiles")
                    if self.profiles is not None and self.session is not None:
                        self.profile_username = QLineEdit()
                        self.profile_username.setObjectName("newProfileUsername")
                        self.profile_username.setPlaceholderText("Child username (e.g. eden_demo)")
                        self.profile_username.setAccessibleName("Child username")
                        self.buttons.addWidget(self.profile_username)
                        self.profile_name = QLineEdit()
                        self.profile_name.setObjectName("newProfileName")
                        self.profile_name.setPlaceholderText("Child display name")
                        self.profile_name.setAccessibleName("Child display name")
                        self.buttons.addWidget(self.profile_name)
                        self.profile_avatar = QComboBox()
                        self.profile_avatar.setObjectName("newProfileAvatar")
                        self.profile_avatar.setAccessibleName("Choose approved character")
                        self.profile_avatar.addItems(SELECTABLE_AVATARS)
                        self.buttons.addWidget(self.profile_avatar)
                        action("Create child profile", self.create_profile)
                        if self.profiles.get(self.state.child_id) is not None:
                            self.buttons.addWidget(QLabel("Activities for current child"))
                            enabled = ActivityPreferences(self.session, self.profiles).load(self.state.child_id)
                            checks_widget = QWidget()
                            checks_grid = QGridLayout(checks_widget)
                            for index, activity in enumerate(ACTIVITIES):
                                checkbox = QCheckBox(activity.replace("-", " ").title())
                                checkbox.setObjectName("activity_" + activity)
                                checkbox.setAccessibleName("Enable " + activity.replace("-", " "))
                                checkbox.setChecked(enabled.get(activity, True))
                                self.activity_checks[activity] = checkbox
                                checks_grid.addWidget(checkbox, index // 4, index % 4)
                            self.buttons.addWidget(checks_widget)
                            action("Save activity choices", self.save_activities)
                            self.buttons.addWidget(QLabel("Parent-controlled sticker rewards"))
                            self.parent_reward_combo = QComboBox()
                            self.parent_reward_combo.setAccessibleName("Choose a sticker to unlock for this child")
                            manifest_path = Path(__file__).resolve().parent.parent / "assets" / "stickers" / "manifest.json"
                            for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["items"]:
                                self.parent_reward_combo.addItem(entry["name"], entry["sku"])
                            self.buttons.addWidget(self.parent_reward_combo)
                            action("Parent unlock selected sticker", self.parent_unlock_sticker)
                elif self.pin_adapter:
                    self.pin_input = QLineEdit()
                    self.pin_input.setObjectName("parentPinInput")
                    self.pin_input.setAccessibleName("Parent PIN")
                    self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
                    self.pin_input.setPlaceholderText("Parent PIN (4–8 digits)")
                    self.pin_input.setMaxLength(8)
                    self.buttons.addWidget(self.pin_input)
                    if self.pin_adapter.has_pin():
                        action("Unlock Parent Corner", self.submit_pin)
                    else:
                        self.pin_confirm = QLineEdit()
                        self.pin_confirm.setObjectName("parentPinConfirm")
                        self.pin_confirm.setAccessibleName("Confirm Parent PIN")
                        self.pin_confirm.setEchoMode(QLineEdit.EchoMode.Password)
                        self.pin_confirm.setPlaceholderText("Confirm Parent PIN")
                        self.pin_confirm.setMaxLength(8)
                        self.buttons.addWidget(self.pin_confirm)
                        action("Set first Parent PIN (demo only)", self.setup_pin)
                else:
                    self.info.setText("Parent Corner locked — PIN adapter not configured")
                if self.state.child_id is None:
                    action("Back to profiles", lambda: self.transition(self.state.logout()))
                else:
                    action("Back to child home", lambda: self.transition(NavigationState(page="home", child_id=self.state.child_id)))
                action("Log out", lambda: self.transition(self.state.logout()))
            self.buttons.activate()
            required_height = self.buttons.contentsMargins().top() + self.buttons.contentsMargins().bottom()
            for index in range(self.buttons.count()):
                widget = self.buttons.itemAt(index).widget()
                if widget is not None:
                    required_height += max(widget.minimumHeight(), widget.sizeHint().height())
            required_height += max(0, self.buttons.count() - 1) * self.buttons.spacing()
            self.controls_widget.setMinimumHeight(required_height)
            self.controls_widget.adjustSize()
            self.controls_widget.updateGeometry()
    return EdenNativeWindow()

def main():
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from .approved_pin import ApprovedPinAdapter
    from .profiles import ProfileRepository
    # Explicit preview-only paths: never share live Eden OS configuration or profiles.
    base = Path.home() / ".eden-native-preview"
    preview_env = {"XDG_CONFIG_HOME": str(base / "config"), "XDG_DATA_HOME": str(base / "data"), "XDG_CACHE_HOME": str(base / "cache"),
                   "APPDATA": str(base / "config"), "LOCALAPPDATA": str(base / "data")}
    platform = detect_platform(environ=preview_env)
    pin_source = Path(__file__).resolve().parent / "approved_models" / "parent_pin.py"
    window = create_window(pin_adapter=ApprovedPinAdapter(platform, pin_source), profiles=ProfileRepository(platform))
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())

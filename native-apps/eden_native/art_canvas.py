"""Native Qt drawing surface; preserved iMac ArtBoard remains the sticker model."""
from pathlib import Path
from collections import Counter
import json
import math
import os
import stat
import tempfile
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QImage
from PySide6.QtWidgets import QWidget

BACKGROUNDS = {"White": "#ffffff", "Sky": "#e4f2ff", "Grass": "#e8f7e7", "Peach": "#fff0dc"}

PALETTE = {
    "Blue": "#2964d4", "Green": "#268754", "Pink": "#d7478a",
    "Purple": "#7650b5", "Black": "#202936", "Red": "#e3292c",
    "Orange": "#fa7a1f", "Yellow": "#f9c719", "Brown": "#78482e",
}

class ArtCanvas(QWidget):
    sticker_layer_changed = Signal()
    sticker_collection_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("artStudioDrawingCanvas")
        self.setAccessibleName("Art Studio drawing canvas")
        self.setAccessibleDescription("Use Tab to focus; numbers 1 to 9 select a sticker; arrows move it; Page Up or Page Down changes its layer; Delete removes the selected sticker; Control Z undoes and Control Shift Z redoes the last action")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(440, 220)
        self.setMouseTracking(True)
        self.strokes = []
        self.redo_strokes = []
        self.active = None
        self.colour = "Blue"
        self.stroke_width = 6
        self.background = QColor("white")
        self.sticker_paths = []
        self.sticker_skus = []
        self.sticker_positions = []
        self.drag_sticker = None
        self.selected_sticker = None
        self.brush_mode = "paint"
        self.sticker_move_undo = []
        self.sticker_move_redo = []
        self._drag_origin = None
        self.action_undo = []
        self.action_redo = []

    def _record_action(self, kind, payload):
        self.action_undo.append((kind, payload))
        if len(self.action_undo) > 500:
            self.action_undo.pop(0)
        self.action_redo.clear()

    def undo_action(self):
        if not self.action_undo:
            return False
        kind, payload = self.action_undo[-1]
        if kind == "stroke":
            if not self.strokes:
                return False
            self.strokes.pop()
        elif kind == "sticker_layer":
            index, target = payload
            if max(index, target) >= len(self.sticker_paths):
                return False
            self._swap_sticker_layers(index, target)
            self.sticker_layer_changed.emit()
        elif kind == "sticker_remove":
            index, path, sku, position = payload
            if len(self.sticker_paths) >= 24:
                return False
            self.sticker_paths.insert(index, path)
            if sku is not None:
                self.sticker_skus.insert(index, sku)
            self.sticker_positions.insert(index, position[:])
            self.sticker_collection_changed.emit()
        elif kind == "sticker_add":
            index, path, sku, position = payload
            if index >= len(self.sticker_paths):
                return False
            self.sticker_paths.pop(index)
            if self.sticker_skus:
                self.sticker_skus.pop(index)
            self.sticker_positions.pop(index)
            self.selected_sticker = None
            self.sticker_collection_changed.emit()
        elif kind == "background":
            self.background = QColor(BACKGROUNDS[payload[0]])
        elif kind == "sticker_move":
            index, before, after = payload
            if index >= len(self.sticker_positions):
                return False
            self.sticker_positions[index] = before[:]
        else:
            return False
        self.action_undo.pop()
        self.action_redo.append((kind, payload))
        self.update()
        return True

    def redo_action(self):
        if not self.action_redo:
            return False
        kind, payload = self.action_redo[-1]
        if kind == "stroke":
            self.strokes.append(payload)
        elif kind == "sticker_layer":
            index, target = payload
            if max(index, target) >= len(self.sticker_paths):
                return False
            self._swap_sticker_layers(index, target)
            self.sticker_layer_changed.emit()
        elif kind == "sticker_remove":
            index, path, sku, position = payload
            if index >= len(self.sticker_paths):
                return False
            self.sticker_paths.pop(index)
            if self.sticker_skus:
                self.sticker_skus.pop(index)
            self.sticker_positions.pop(index)
            self.selected_sticker = None
            self.sticker_collection_changed.emit()
        elif kind == "sticker_add":
            index, path, sku, position = payload
            if len(self.sticker_paths) >= 24:
                return False
            self.sticker_paths.insert(index, path)
            if sku is not None:
                self.sticker_skus.insert(index, sku)
            self.sticker_positions.insert(index, position[:])
            self.sticker_collection_changed.emit()
        elif kind == "background":
            self.background = QColor(BACKGROUNDS[payload[1]])
        elif kind == "sticker_move":
            index, before, after = payload
            if index >= len(self.sticker_positions):
                return False
            self.sticker_positions[index] = after[:]
        else:
            return False
        self.action_redo.pop()
        self.action_undo.append((kind, payload))
        self.update()
        return True

    def set_stickers(self, paths, skus=None):
        next_paths = [Path(path) for path in paths[:24]]
        next_skus = list(skus[:24]) if skus is not None else []
        if next_skus and len(next_skus) != len(next_paths):
            raise ValueError("Sticker identifiers and images do not match")
        self.sticker_paths = next_paths
        self.sticker_skus = next_skus
        while len(self.sticker_positions) < len(self.sticker_paths):
            index = len(self.sticker_positions)
            self.sticker_positions.append([min(.85, .05 + (index % 5) * .19), min(.82, .07 + (index // 5) * .20)])
        self.sticker_positions = self.sticker_positions[:len(self.sticker_paths)]
        self.sticker_move_undo.clear()
        self.sticker_move_redo.clear()
        self.action_undo.clear()
        self.action_redo.clear()
        if self.selected_sticker is not None and self.selected_sticker >= len(self.sticker_paths):
            self.selected_sticker = None
        self.update()

    def add_sticker(self, path, sku):
        if len(self.sticker_paths) >= 24 or not isinstance(sku, str) or not sku:
            return False
        index = len(self.sticker_paths)
        position = [min(.85, .05 + (index % 5) * .19), min(.82, .07 + (index // 5) * .20)]
        self.sticker_paths.append(Path(path))
        self.sticker_skus.append(sku)
        self.sticker_positions.append(position[:])
        self._record_action("sticker_add", (index, Path(path), sku, position[:]))
        self.sticker_collection_changed.emit()
        self.update()
        return True

    def remove_selected_sticker(self):
        index = self.selected_sticker
        if index is None or not 0 <= index < len(self.sticker_paths):
            return False
        path = self.sticker_paths.pop(index)
        sku = self.sticker_skus.pop(index) if self.sticker_skus else None
        position = self.sticker_positions.pop(index)
        self.selected_sticker = None
        self._record_action("sticker_remove", (index, path, sku, position[:]))
        self.sticker_collection_changed.emit()
        self.update()
        return True

    def remove_last_sticker(self):
        if not self.sticker_paths:
            return False
        self.selected_sticker = len(self.sticker_paths) - 1
        return self.remove_selected_sticker()

    def _sticker_at(self, point):
        for index in range(len(self.sticker_paths) - 1, -1, -1):
            x, y = self.sticker_positions[index]
            if x <= point[0] <= x + 54/max(1, self.width()) and y <= point[1] <= y + 54/max(1, self.height()):
                return index
        return None

    def _swap_sticker_layers(self, index, target):
        self.sticker_paths[index], self.sticker_paths[target] = self.sticker_paths[target], self.sticker_paths[index]
        if self.sticker_skus:
            self.sticker_skus[index], self.sticker_skus[target] = self.sticker_skus[target], self.sticker_skus[index]
        self.sticker_positions[index], self.sticker_positions[target] = self.sticker_positions[target], self.sticker_positions[index]
        self.selected_sticker = target if self.selected_sticker == index else index if self.selected_sticker == target else self.selected_sticker

    def move_selected_sticker_layer(self, direction):
        """Move selected sticker forward/back one layer, keeping its saved position."""
        if direction not in (-1, 1):
            raise ValueError("Layer direction must be -1 or 1")
        index = self.selected_sticker
        if index is None or not 0 <= index < len(self.sticker_paths):
            return False
        target = index + direction
        if not 0 <= target < len(self.sticker_paths):
            return False
        self._swap_sticker_layers(index, target)
        self.sticker_move_undo.clear()
        self.sticker_move_redo.clear()
        self._record_action("sticker_layer", (index, target))
        self.update()
        self.sticker_layer_changed.emit()
        return True

    def set_background(self, name):
        if name not in BACKGROUNDS:
            raise ValueError("Unknown background")
        previous = next((key for key, colour in BACKGROUNDS.items() if self.background.name() == colour), "White")
        if previous == name:
            return
        self.background = QColor(BACKGROUNDS[name])
        self._record_action("background", (previous, name))
        self.update()

    def set_brush_width(self, width):
        if width not in (3, 4, 6, 12, 13, 20):
            raise ValueError("Unsupported brush size")
        self.stroke_width = width

    def set_eraser(self, enabled=True):
        self.brush_mode = "erase" if enabled else "paint"

    def set_colour(self, name):
        if name not in PALETTE:
            raise ValueError("Unknown colour")
        self.colour = name
        self.brush_mode = "paint"

    def _point(self, event):
        pos = event.position()
        return (max(0.0, min(1.0, pos.x() / max(1, self.width()))),
                max(0.0, min(1.0, pos.y() / max(1, self.height()))))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_sticker = self._sticker_at(self._point(event))
            if self.drag_sticker is not None:
                self.selected_sticker = self.drag_sticker
                self._drag_origin = self.sticker_positions[self.drag_sticker][:]
                return
        if event.button() == Qt.MouseButton.LeftButton and len(self.strokes) < 500:
            self.active = {"colour": self.colour, "width": self.stroke_width, "points": [self._point(event)], "mode": self.brush_mode}
            self.update()

    def mouseMoveEvent(self, event):
        if self.drag_sticker is not None:
            x, y = self._point(event)
            self.sticker_positions[self.drag_sticker] = [min(x, max(0, 1-54/max(1,self.width()))), min(y, max(0, 1-54/max(1,self.height())))]
            self.update()
            return
        if self.active is not None and len(self.active["points"]) < 2000:
            self.active["points"].append(self._point(event))
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drag_sticker is not None:
            index = self.drag_sticker
            before = self._drag_origin
            after = self.sticker_positions[index][:]
            self.drag_sticker = None
            self._drag_origin = None
            if before is not None and before != after:
                self._remember_sticker_move(index, before, after)
            self.update()
            return
        if self.active is not None:
            self.active["points"].append(self._point(event))
            self.strokes.append(self.active)
            self._record_action("stroke", self.active)
            self.redo_strokes.clear()
            self.active = None
            self.update()

    def _remember_sticker_move(self, index, before, after):
        self.sticker_move_undo.append((index, before[:], after[:]))
        if len(self.sticker_move_undo) > 100:
            self.sticker_move_undo.pop(0)
        self.sticker_move_redo.clear()
        self._record_action("sticker_move", (index, before[:], after[:]))

    def undo_sticker_move(self):
        if not self.action_undo or self.action_undo[-1][0] != "sticker_move":
            return False
        return self.undo_action()

    def redo_sticker_move(self):
        if not self.action_redo or self.action_redo[-1][0] != "sticker_move":
            return False
        return self.redo_action()

    def undo(self):
        if not self.action_undo or self.action_undo[-1][0] != "stroke":
            return False
        return self.undo_action()

    def redo(self):
        if not self.action_redo or self.action_redo[-1][0] != "stroke":
            return False
        return self.redo_action()

    def clear(self):
        self.strokes.clear()
        self.redo_strokes.clear()
        self.action_undo.clear()
        self.action_redo.clear()
        self.active = None
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Z:
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    self.redo_action()
                else:
                    self.undo_action()
                event.accept()
                return
            if key == Qt.Key.Key_Y:
                self.redo_action()
                event.accept()
                return
        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and modifiers == Qt.KeyboardModifier.NoModifier:
            self.remove_selected_sticker()
            event.accept()
            return
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            index = key - Qt.Key.Key_1
            if index < len(self.sticker_positions):
                self.selected_sticker = index
                self.update()
                event.accept()
                return
        if key in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            self.move_selected_sticker_layer(1 if key == Qt.Key.Key_PageUp else -1)
            event.accept()
            return
        movements = {Qt.Key.Key_Left: (-.025, 0), Qt.Key.Key_Right: (.025, 0),
                     Qt.Key.Key_Up: (0, -.025), Qt.Key.Key_Down: (0, .025)}
        if key in movements and self.selected_sticker is not None and self.selected_sticker < len(self.sticker_positions):
            dx, dy = movements[key]
            x, y = self.sticker_positions[self.selected_sticker]
            before = [x, y]
            after = [max(0, min(1 - 54/max(1, self.width()), x+dx)),
                     max(0, min(1 - 54/max(1, self.height()), y+dy))]
            self.sticker_positions[self.selected_sticker] = after
            if before != after:
                self._remember_sticker_move(self.selected_sticker, before, after)
            self.update()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.background)
        # Keep drawing marks on a transparent layer so erasing reveals the
        # CURRENT background, even after the child changes backgrounds.
        layer = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        layer.fill(Qt.GlobalColor.transparent)
        ink = QPainter(layer)
        ink.setRenderHint(QPainter.RenderHint.Antialiasing)
        for stroke in self.strokes + ([self.active] if self.active else []):
            erasing = stroke.get("mode") == "erase"
            ink.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear if erasing
                                   else QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor("black") if erasing else QColor(PALETTE[stroke["colour"]]), stroke["width"],
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            ink.setPen(pen)
            points = [QPointF(x*self.width(), y*self.height()) for x, y in stroke["points"]]
            if len(points) == 1:
                ink.drawPoint(points[0])
            else:
                for first, second in zip(points, points[1:]):
                    ink.drawLine(first, second)
        ink.end()
        painter.drawImage(0, 0, layer)
        for index, path in enumerate(self.sticker_paths):
            if path.is_file() and not path.is_symlink():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    x, y = self.sticker_positions[index]
                    painter.drawPixmap(round(x * self.width()), round(y * self.height()), 54, 54, pixmap)
        painter.end()

    def save_project(self, directory: Path, sticker_skus=()):
        """Save editable strokes and sticker references, never absolute asset paths."""
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        ordered_skus = self.sticker_skus if self.sticker_skus else list(sticker_skus[:24])
        if self.sticker_skus and sticker_skus and Counter(ordered_skus) != Counter(sticker_skus):
            raise ValueError("Sticker entitlement mismatch")
        if len(ordered_skus) > 24 or len(self.sticker_positions) not in (0, len(ordered_skus)):
            raise ValueError("Invalid sticker project state")
        if not all(isinstance(sku, str) and sku.startswith("sticker_") and len(sku) <= 80 for sku in ordered_skus):
            raise ValueError("Invalid sticker project identifiers")
        if not all(isinstance(pos, (list, tuple)) and len(pos) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1 for v in pos) for pos in self.sticker_positions[:len(ordered_skus)]):
            raise ValueError("Invalid sticker project positions")
        payload = {"version": 1, "strokes": self.strokes,
                   "stickers": ordered_skus,
                   "sticker_positions": self.sticker_positions[:len(ordered_skus)],
                   "background": next((name for name, colour in BACKGROUNDS.items() if self.background.name() == colour), "White")}
        destination = directory / "current-art-project.json"
        fd, temporary = tempfile.mkstemp(prefix=".art-", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                json.dump(payload, out)
                out.flush()
                os.fsync(out.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return destination

    def load_project(self, directory: Path, allowed_stickers=None):
        """Validate bounds before applying a saved project. Return sticker SKUs."""
        source = directory / "current-art-project.json"
        if source.is_symlink():
            raise ValueError("Invalid art project file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(source, flags)
        with os.fdopen(fd, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 2_000_000:
                raise ValueError("Invalid art project file")
            content = stream.read(2_000_001)
        if len(content) > 2_000_000:
            raise ValueError("Invalid art project file")
        def reject_nonfinite(value):
            raise ValueError("Non-finite art project number")
        payload = json.loads(content.decode("utf-8"), parse_constant=reject_nonfinite)
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise ValueError("Unsupported art project")
        background = payload.get("background", "White")
        if background not in BACKGROUNDS:
            raise ValueError("Invalid background")
        strokes = payload.get("strokes")
        stickers = payload.get("stickers")
        if not isinstance(strokes, list) or len(strokes) > 500 or not isinstance(stickers, list) or len(stickers) > 24:
            raise ValueError("Invalid art project contents")
        for stroke in strokes:
            if not isinstance(stroke, dict) or stroke.get("colour") not in PALETTE or isinstance(stroke.get("width"), bool) or not isinstance(stroke.get("width"), (int, float)) or not math.isfinite(stroke["width"]) or not 1 <= stroke["width"] <= 28:
                raise ValueError("Invalid stroke")
            if stroke.get("mode", "paint") not in ("paint", "erase"):
                raise ValueError("Invalid brush mode")
            points = stroke.get("points")
            if not isinstance(points, list) or not 1 <= len(points) <= 2000:
                raise ValueError("Invalid points")
            for point in points:
                if not isinstance(point, list) or len(point) != 2 or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1 for v in point):
                    raise ValueError("Invalid coordinates")
        if not all(isinstance(sku, str) and len(sku) <= 80 and sku.startswith("sticker_") for sku in stickers):
            raise ValueError("Invalid sticker reference")
        positions = payload.get("sticker_positions", [])
        if not isinstance(positions, list) or len(positions) not in (0, len(stickers)):
            raise ValueError("Invalid sticker positions")
        if not all(isinstance(pos, list) and len(pos) == 2 and all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1 for v in pos) for pos in positions):
            raise ValueError("Invalid sticker coordinates")
        if allowed_stickers is not None and any(sku not in allowed_stickers for sku in stickers):
            raise ValueError("Sticker not permitted for this child")
        self.background = QColor(BACKGROUNDS[background])
        self.strokes = strokes
        self.sticker_positions = positions
        self.selected_sticker = None
        self.sticker_move_undo.clear()
        self.sticker_move_redo.clear()
        self.redo_strokes.clear()
        self.action_undo.clear()
        self.action_redo.clear()
        self.active = None
        self.update()
        return stickers

    def save_png(self, directory: Path):
        """Create a numbered picture without following links or overwriting files."""
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temporary = tempfile.mkstemp(prefix=".eden-art-", suffix=".png", dir=directory)
        try:
            os.close(fd)
            if not self.grab().save(temporary, "PNG"):
                raise OSError("Could not save artwork")
            os.chmod(temporary, 0o600)
            for i in range(1, 10001):
                output = directory / f"eden-art-{i:04d}.png"
                try:
                    os.link(temporary, output, follow_symlinks=False)
                    return output
                except FileExistsError:
                    continue
            raise OSError("Art Studio save limit reached")
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

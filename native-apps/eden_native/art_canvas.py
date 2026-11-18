"""Native Qt drawing surface; preserved iMac ArtBoard remains the sticker model."""
from pathlib import Path
import json
import os
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("artStudioDrawingCanvas")
        self.setAccessibleName("Art Studio drawing canvas")
        self.setAccessibleDescription("Use Tab to focus, number keys 1 to 9 to select a sticker, arrow keys to move it, and Page Up or Page Down to change its layer")
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

    def set_stickers(self, paths, skus=None):
        self.sticker_paths = list(paths[:24])
        self.sticker_skus = list(skus[:24]) if skus is not None else []
        if self.sticker_skus and len(self.sticker_skus) != len(self.sticker_paths):
            raise ValueError("Sticker identifiers and images do not match")
        while len(self.sticker_positions) < len(self.sticker_paths):
            index = len(self.sticker_positions)
            self.sticker_positions.append([min(.85, .05 + (index % 5) * .19), min(.82, .07 + (index // 5) * .20)])
        self.sticker_positions = self.sticker_positions[:len(self.sticker_paths)]
        if self.selected_sticker is not None and self.selected_sticker >= len(self.sticker_paths):
            self.selected_sticker = None
        self.update()

    def _sticker_at(self, point):
        for index in range(len(self.sticker_paths) - 1, -1, -1):
            x, y = self.sticker_positions[index]
            if x <= point[0] <= x + 54/max(1, self.width()) and y <= point[1] <= y + 54/max(1, self.height()):
                return index
        return None

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
        self.sticker_paths[index], self.sticker_paths[target] = self.sticker_paths[target], self.sticker_paths[index]
        if self.sticker_skus:
            self.sticker_skus[index], self.sticker_skus[target] = self.sticker_skus[target], self.sticker_skus[index]
        self.sticker_positions[index], self.sticker_positions[target] = self.sticker_positions[target], self.sticker_positions[index]
        self.selected_sticker = target
        self.update()
        self.sticker_layer_changed.emit()
        return True

    def set_background(self, name):
        if name not in BACKGROUNDS:
            raise ValueError("Unknown background")
        self.background = QColor(BACKGROUNDS[name])
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
            self.drag_sticker = None
            self.update()
            return
        if self.active is not None:
            self.active["points"].append(self._point(event))
            self.strokes.append(self.active)
            self.redo_strokes.clear()
            self.active = None
            self.update()

    def undo(self):
        if self.strokes:
            self.redo_strokes.append(self.strokes.pop())
            self.update()

    def redo(self):
        if self.redo_strokes:
            self.strokes.append(self.redo_strokes.pop())
            self.update()

    def clear(self):
        self.strokes.clear()
        self.redo_strokes.clear()
        self.active = None
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
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
            self.sticker_positions[self.selected_sticker] = [max(0, min(1 - 54/max(1, self.width()), x+dx)),
                                                             max(0, min(1 - 54/max(1, self.height()), y+dy))]
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
        if self.sticker_skus and sticker_skus and set(ordered_skus) != set(sticker_skus):
            raise ValueError("Sticker entitlement mismatch")
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
        if source.is_symlink() or source.stat().st_size > 2_000_000:
            raise ValueError("Invalid art project file")
        payload = json.loads(source.read_text(encoding="utf-8"))
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
            if not isinstance(stroke, dict) or stroke.get("colour") not in PALETTE or not isinstance(stroke.get("width"), (int, float)) or not 1 <= stroke["width"] <= 28:
                raise ValueError("Invalid stroke")
            if stroke.get("mode", "paint") not in ("paint", "erase"):
                raise ValueError("Invalid brush mode")
            points = stroke.get("points")
            if not isinstance(points, list) or len(points) > 2000:
                raise ValueError("Invalid points")
            for point in points:
                if not isinstance(point, list) or len(point) != 2 or not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in point):
                    raise ValueError("Invalid coordinates")
        if not all(isinstance(sku, str) and len(sku) <= 80 and sku.startswith("sticker_") for sku in stickers):
            raise ValueError("Invalid sticker reference")
        positions = payload.get("sticker_positions", [])
        if not isinstance(positions, list) or len(positions) not in (0, len(stickers)):
            raise ValueError("Invalid sticker positions")
        if not all(isinstance(pos, list) and len(pos) == 2 and all(isinstance(v, (float, int)) and not isinstance(v, bool) and 0 <= v <= 1 for v in pos) for pos in positions):
            raise ValueError("Invalid sticker coordinates")
        if allowed_stickers is not None and any(sku not in allowed_stickers for sku in stickers):
            raise ValueError("Sticker not permitted for this child")
        self.background = QColor(BACKGROUNDS[background])
        self.strokes = strokes
        self.sticker_positions = positions
        self.selected_sticker = None
        self.redo_strokes.clear()
        self.active = None
        self.update()
        return stickers

    def save_png(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        for i in range(1, 10001):
            output = directory / f"eden-art-{i:04d}.png"
            if not output.exists():
                if not self.grab().save(str(output), "PNG"):
                    raise OSError("Could not save artwork")
                return output
        raise OSError("Art Studio save limit reached")

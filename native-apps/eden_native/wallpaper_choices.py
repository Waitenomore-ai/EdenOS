"""Per-child selection of approved native iMac wallpapers."""
import json
import os
from pathlib import Path


class WallpaperChoices:
    def __init__(self, path):
        self.path = Path(path)

    @staticmethod
    def _valid_child(child):
        return isinstance(child, str) and bool(child) and child.replace('_', '').replace('-', '').isalnum()

    def _read(self):
        if self.path.is_symlink():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return {}
        return data if isinstance(data, dict) else {}

    def selected(self, child, approved):
        if not self._valid_child(child):
            return None
        candidate = self._read().get(child)
        return candidate if isinstance(candidate, str) and candidate in approved else None

    def choose(self, child, filename, approved):
        if not self._valid_child(child) or not isinstance(filename, str) or filename not in approved:
            return False
        if filename != Path(filename).name or not filename.lower().endswith('.png'):
            return False
        if self.path.is_symlink():
            return False
        data = self._read()
        data[child] = filename
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_name(self.path.name + '.tmp')
        if temp.exists() or temp.is_symlink():
            return False
        descriptor = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                json.dump(data, stream, sort_keys=True)
            os.replace(temp, self.path)
        except OSError:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass
            return False
        return True

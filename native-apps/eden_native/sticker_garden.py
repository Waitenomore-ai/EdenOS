"""Offline child-scoped Sticker Garden placements (staging only)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile

SLOTS = 24


def load_garden(path: Path, allowed: set[str]) -> dict[int, str]:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        return {}
    try:
        if path.stat().st_size > 8192:
            return {}
        with path.open('rb') as stream:
            data = stream.read(8193)
        if len(data) > 8192:
            return {}
        payload = json.loads(data)
        if not isinstance(payload, dict) or payload.get('version') != 1 or not isinstance(payload.get('placements'), list):
            return {}
        placements = {}
        for item in payload['placements']:
            if not isinstance(item, dict) or type(item.get('slot')) is not int or not 0 <= item['slot'] < SLOTS:
                return {}
            sku = item.get('sku')
            if not isinstance(sku, str) or sku not in allowed or item['slot'] in placements:
                return {}
            placements[item['slot']] = sku
        return placements
    except (OSError, UnicodeError, ValueError, TypeError):
        return {}


def save_garden(path: Path, placements: dict[int, str], allowed: set[str]) -> None:
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Refusing linked Sticker Garden file')
    if len(placements) > SLOTS or any(type(slot) is not int or not 0 <= slot < SLOTS or not isinstance(sku, str) or sku not in allowed for slot, sku in placements.items()):
        raise ValueError('Invalid Sticker Garden placements')
    data = json.dumps({'version': 1, 'placements': [{'slot': slot, 'sku': sku} for slot, sku in sorted(placements.items())]}, separators=(',', ':')).encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.garden-', suffix='.tmp', delete=False) as stream:
            temp_name = stream.name
            os.chmod(temp_name, 0o600)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_symlink():
            raise ValueError('Refusing linked Sticker Garden file')
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)

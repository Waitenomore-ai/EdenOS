"""Shared Find Eden asset validation and daily image selection."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import struct

EPOCH = dt.date(2026, 10, 31)
INSTALLED_PACK = Path('/usr/share/eden-os/find-eden')

def default_pack():
    return INSTALLED_PACK if INSTALLED_PACK.is_dir() else Path(__file__).resolve().parents[2] / 'find-eden'

def read_manifest(pack, verify_hashes=True):
    pack = Path(pack).resolve()
    try:
        rows = json.loads((pack/'wallpapers.json').read_text())
        if not isinstance(rows,list) or len(rows) != 28:
            raise ValueError('Find Eden needs all 28 wallpaper scenes')
        seen = set()
        paths = []
        for row in rows:
            if not isinstance(row,dict) or not isinstance(row.get('file'),str):
                raise ValueError('Invalid Find Eden manifest entry')
            relative = Path(row['file'])
            image = (pack/relative).resolve()
            if relative.is_absolute() or '..' in relative.parts or not image.is_relative_to(pack) or image in seen:
                raise ValueError('Invalid Find Eden wallpaper path')
            seen.add(image)
            with image.open('rb') as source:
                header = source.read(24)
            if len(header)!=24 or header[:8]!=b'\x89PNG\r\n\x1a\n' or header[12:16]!=b'IHDR' or struct.unpack('>II',header[16:24])!=(1672,941):
                raise ValueError('Invalid Find Eden PNG dimensions')
            if verify_hashes and hashlib.sha256(image.read_bytes()).hexdigest() != row.get('sha256'):
                raise ValueError('Find Eden wallpaper checksum mismatch')
            paths.append(image)
        if not (pack/'Find-Eden.html').is_file() or not (pack/'daily-wallpaper/rotator.py').is_file():
            raise ValueError('Find Eden game or daily changer is missing')
        return rows, paths
    except (OSError,TypeError,KeyError,json.JSONDecodeError) as exc:
        raise ValueError('Cannot load the complete Find Eden pack') from exc

def today_image(pack=None, day=None):
    pack = Path(pack) if pack is not None else default_pack()
    _, paths = read_manifest(pack, verify_hashes=False)
    return paths[((day or dt.date.today())-EPOCH).days % len(paths)]

def stage_pack(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    rows, images = read_manifest(source)
    if destination == source or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError('Asset staging must use a separate destination')
    destination.mkdir(parents=True,exist_ok=True)
    for name in ('wallpapers.json','Find-Eden.html','README.md','daily-wallpaper/rotator.py'):
        src = source/name
        if src.is_file():
            dst = destination/name
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dst)
    for row,image in zip(rows,images):
        dst=destination/row['file'];dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(image,dst)
    # Git checkouts/build umasks must not make installed child assets root-only.
    destination.chmod(0o755)
    for path in destination.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)


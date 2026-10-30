"""Read non-personal build identification embedded in the image."""
import json
from pathlib import Path

BUILD_PATH = Path('/etc/eden-os/build.json')


def build_label(path: Path = BUILD_PATH) -> str:
    fallback = 'Development build — version unavailable'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return fallback
    if not isinstance(data, dict):
        return fallback
    values = [data.get(key) for key in ('version', 'commit', 'built_at')]
    if any(not isinstance(value, str) or not value or len(value) > 100
           or not value.isprintable() for value in values):
        return fallback
    version, commit, built_at = values
    return f'EdenOS {version} · {commit[:12]} · {built_at}'

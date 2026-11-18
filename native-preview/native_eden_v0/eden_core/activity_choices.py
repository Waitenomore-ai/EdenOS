"""iMac-compatible, per-child launcher restrictions.

This is a launcher preference, not an operating-system security boundary.
No child data is bundled into a native installer.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .activity_visibility import REVIEWED_RATINGS


def _validated_path(root: Path, username: str, valid_usernames) -> Path:
    if (not isinstance(username, str) or
            username not in set(valid_usernames) or
            "/" in username or "\\" in username or username in (".", "..")):
        raise ValueError("Unknown child")
    return Path(root) / "activity-choices" / (username + ".json")


def read_choices(root: Path, username: str, valid_usernames) -> dict[str, bool]:
    """Read existing iMac format without creating or migrating data."""
    try:
        p = _validated_path(root, username, valid_usernames)
        data = json.loads(p.read_text(encoding="utf-8"))
        enabled = data.get("enabled")
        if data.get("version") != 1 or not isinstance(enabled, dict):
            return {}
        if any(not isinstance(k, str) or not isinstance(v, bool) for k, v in enabled.items()):
            return {}
        return {k: v for k, v in enabled.items() if k in REVIEWED_RATINGS}
    except (OSError, ValueError, TypeError, AttributeError):
        return {}


def save_choices(root: Path, username: str, choices: dict[str, bool],
                 valid_usernames, *, parent_unlocked: bool) -> None:
    """Require Parent Corner unlock and atomically write private choices."""
    if not parent_unlocked:
        raise PermissionError("Unlock Parent Corner first")
    target = _validated_path(root, username, valid_usernames)
    if (not isinstance(choices, dict) or
            any(k not in REVIEWED_RATINGS or not isinstance(v, bool)
                for k, v in choices.items())):
        raise ValueError("Invalid activity settings")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=".activity-", dir=target.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump({"version": 1, "enabled": choices}, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

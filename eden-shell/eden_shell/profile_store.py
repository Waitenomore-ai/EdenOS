"""Private, local storage for child greeter profile cards."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from .profile_cards import ProfileCard, make_profile_card


def load_profiles(path: Path) -> tuple[ProfileCard, ...]:
    """Load valid profiles, returning no profiles when the file is unsafe."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        records = document["profiles"]
        if not isinstance(records, list):
            return ()
        profiles = tuple(
            make_profile_card(record["username"], record["display_name"], record["avatar"])
            for record in records
        )
        if len({profile.username for profile in profiles}) != len(profiles):
            return ()
        return profiles
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return ()


def save_profiles(profiles: list[ProfileCard] | tuple[ProfileCard, ...], path: Path) -> None:
    """Atomically save only validated greeter metadata with private permissions."""
    if len({profile.username for profile in profiles}) != len(profiles):
        raise ValueError("Profile usernames must be unique.")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    document = {
        "profiles": [
            {
                "username": profile.username,
                "display_name": profile.display_name,
                "avatar": profile.avatar,
            }
            for profile in profiles
        ]
    }
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def remove_profile(username: str, path: Path) -> bool:
    """Remove one profile and report whether it existed."""
    profiles = list(load_profiles(path))
    remaining = [profile for profile in profiles if profile.username != username]
    if len(remaining) == len(profiles):
        return False
    save_profiles(remaining, path)
    return True

"""Read-only lookup of the approved Eden OS local profile file.

Never creates directories, migrates profiles or bundles child records.
"""
from __future__ import annotations

from pathlib import Path

from .profile_source import read_profile_cards


def find_existing_profiles(home: Path | None = None) -> Path | None:
    """Return the existing validated source, or None for safe demo mode."""
    home = Path.home() if home is None else Path(home)
    candidate = home / ".config" / "eden-os" / "profiles.json"
    if candidate.is_file() and read_profile_cards(candidate):
        return candidate
    return None

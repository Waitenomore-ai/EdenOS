"""Approved avatar file resolver: exact IDs only, no path injection."""
from pathlib import Path
from .approved_models.profile_cards import SELECTABLE_AVATARS

DEFAULT_AVATAR_ROOT = Path(__file__).resolve().parent.parent / "assets" / "avatars"

def resolve_avatar(avatar: str, root: Path = DEFAULT_AVATAR_ROOT) -> Path | None:
    if avatar not in SELECTABLE_AVATARS:
        return None
    path = Path(root) / (avatar + ".png")
    return path if path.is_file() and not path.is_symlink() else None

"""Validation for local child profile cards used by a future greeter."""

from __future__ import annotations

from dataclasses import dataclass
import re


AVATARS = (
    "sun",
    "moon",
    "butterfly",
    "tree",
    "rainbow",
    "flower",
)
_USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,30}$")


@dataclass(frozen=True)
class ProfileCard:
    username: str
    display_name: str
    avatar: str


def make_profile_card(username: str, display_name: str, avatar: str) -> ProfileCard:
    """Validate greeter-safe metadata; never accept a custom file path."""
    if not _USERNAME.fullmatch(username):
        raise ValueError("Profile username is not valid.")
    display_name = display_name.strip()
    if not display_name or len(display_name) > 40 or not display_name.isprintable():
        raise ValueError("Choose a readable display name between 1 and 40 characters.")
    if avatar not in AVATARS:
        raise ValueError("Choose one of the included Eden avatars.")
    return ProfileCard(username, display_name, avatar)


def public_card(card: ProfileCard) -> dict[str, str]:
    """Return only fields a picture-based greeter may display."""
    return {"display_name": card.display_name, "avatar": card.avatar}

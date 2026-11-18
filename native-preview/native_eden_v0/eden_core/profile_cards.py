"""Validation for local child profile cards used by a future greeter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re


AVATAR_SUBJECTS = (
    "child-1", "child-2", "child-3", "child-4",
    "child-5", "child-6", "child-7", "child-8",
    "fox", "rabbit", "robin", "hedgehog",
)
PORTRAIT_AVATARS = tuple(
    f"{style}-{number:02d}-{subject}"
    for style in ("plain", "wreath")
    for number, subject in enumerate(AVATAR_SUBJECTS, 1)
)
LEGACY_AVATARS = ("sun", "moon", "butterfly", "tree", "rainbow", "flower")
APPROVED_AVATARS = ('approved-eden', 'approved-colby', 'approved-mila', 'approved-jack', 'approved-mark', 'approved-jessica', 'approved-arjun', 'approved-priya', 'approved-kai', 'approved-mei', 'approved-katie',)
AVATARS = LEGACY_AVATARS + PORTRAIT_AVATARS + APPROVED_AVATARS
SELECTABLE_AVATARS = APPROVED_AVATARS

_CHARACTER_NAMES = {
    "plain-01-child-1": "Eden",
    "plain-02-child-2": "Billy",
    "plain-03-child-3": "Sophie",
    "plain-04-child-4": "Oliver",
    "plain-05-child-5": "Maya",
    "plain-06-child-6": "Freddie",
    "plain-07-child-7": "Rosie",
    "plain-08-child-8": "Amara",
    "plain-09-fox": "Freddie Fox",
    "plain-10-rabbit": "Roger Rabbit",
    "plain-11-robin": "Robbie Robin",
    "plain-12-hedgehog": "Harry Hedgehog",
}


def avatar_label(name):
    if name in APPROVED_AVATARS:
        return name.removeprefix("approved-").title()
    if name in PORTRAIT_AVATARS:
        style, number, subject = name.split("-", 2)
        plain_key = f"plain-{number}-{subject}"
        title = _CHARACTER_NAMES[plain_key]
        return title + (" — garden wreath" if style == "wreath" else "")
    return name.title()

_USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,30}$")


@dataclass(frozen=True)
class ProfileCard:
    username: str
    display_name: str
    avatar: str
    date_of_birth: str | None = None


def make_profile_card(username: str, display_name: str, avatar: str, date_of_birth: str | None = None) -> ProfileCard:
    """Validate greeter-safe metadata; never accept a custom file path."""
    if not _USERNAME.fullmatch(username):
        raise ValueError("Profile username is not valid.")
    display_name = display_name.strip()
    if not display_name or len(display_name) > 40 or not display_name.isprintable():
        raise ValueError("Choose a readable display name between 1 and 40 characters.")
    if avatar not in AVATARS:
        raise ValueError("Choose one of the included Eden avatars.")
    if date_of_birth is not None:
        if not isinstance(date_of_birth, str):
            raise ValueError("Invalid date of birth")
        try:
            parsed = date.fromisoformat(date_of_birth)
        except ValueError as exc:
            raise ValueError("Invalid date of birth") from exc
        from .age_policy import ChildAge
        ChildAge(date_of_birth=parsed)
    return ProfileCard(username, display_name, avatar, date_of_birth)


def public_card(card: ProfileCard) -> dict[str, str]:
    """Return only fields a picture-based greeter may display."""
    return {"display_name": card.display_name, "avatar": card.avatar}

"""Validation for the adult-led child profile form."""

from __future__ import annotations

import re
from dataclasses import dataclass


_USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,30}$")


@dataclass(frozen=True)
class ChildProfile:
    nickname: str
    username: str


def validate_child_profile(
    nickname: str, username: str, password: str, password_confirmation: str
) -> ChildProfile:
    """Validate only the details needed for a local standard account."""
    nickname = nickname.strip()
    if not nickname or len(nickname) > 40 or not nickname.isprintable():
        raise ValueError("Choose a nickname between 1 and 40 readable characters.")
    if not _USERNAME.fullmatch(username):
        raise ValueError(
            "Use a short username with lowercase letters, numbers, _ or -; start with a letter or _."
        )
    if (
        len(password) < 8
        or len(password) > 128
        or not password.strip()
        or not password.isprintable()
    ):
        raise ValueError("Choose a passphrase between 8 and 128 printable characters.")
    if password != password_confirmation:
        raise ValueError("The two passphrases do not match.")
    return ChildProfile(nickname=nickname, username=username)

"""Adult-facing, side-effect-free editor model for child profile cards."""

from __future__ import annotations

from dataclasses import dataclass

from .profile_cards import AVATARS, ProfileCard, make_profile_card, public_card


@dataclass(frozen=True)
class ProfilePreview:
    username: str
    public_card: dict[str, str]


class ProfileEditor:
    """Edit greeter metadata without changing accounts or writing files."""

    def __init__(self, username: str, display_name: str) -> None:
        initial = make_profile_card(username, display_name, AVATARS[0])
        self._username = initial.username
        self._initial_name = initial.display_name
        self._display_name = initial.display_name
        self._avatar = initial.avatar

    @property
    def avatar(self) -> str:
        return self._avatar

    def set_display_name(self, display_name: str) -> None:
        self._display_name = display_name.strip()

    def choose_avatar(self, avatar: str) -> bool:
        if avatar not in AVATARS:
            return False
        self._avatar = avatar
        return True

    def preview(self) -> ProfilePreview:
        card: ProfileCard = make_profile_card(self._username, self._display_name, self._avatar)
        return ProfilePreview(username=card.username, public_card=public_card(card))

    def reset(self) -> None:
        self._display_name = self._initial_name
        self._avatar = AVATARS[0]

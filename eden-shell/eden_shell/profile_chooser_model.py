"""Safe, offline profile-tile selection for the future Eden greeter."""

from __future__ import annotations

from collections.abc import Iterable

from .profile_cards import ProfileCard, public_card


class ProfileChooser:
    """Keep greeter display data separate from the account selected for login."""

    text_login_available = True

    def __init__(self, profiles: Iterable[ProfileCard]) -> None:
        self._profiles = tuple(profiles)
        self._selected_index: int | None = None

    def tiles(self) -> list[dict[str, str]]:
        """Return only the display name and approved avatar for each tile."""
        return [public_card(profile) for profile in self._profiles]

    def select(self, index: int) -> str | None:
        """Select a tile and return its private account mapping, or clear it."""
        if not isinstance(index, int) or isinstance(index, bool):
            self._selected_index = None
            return None
        if not 0 <= index < len(self._profiles):
            self._selected_index = None
            return None
        self._selected_index = index
        return self._profiles[index].username

    def selected_username(self) -> str | None:
        if self._selected_index is None:
            return None
        return self._profiles[self._selected_index].username

    def selected_public_card(self) -> dict[str, str] | None:
        if self._selected_index is None:
            return None
        return public_card(self._profiles[self._selected_index])

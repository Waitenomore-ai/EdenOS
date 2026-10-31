"""Small, offline nature observation cards for Eden."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NatureItem:
    symbol: str
    label: str
    hint: str


NATURE_ITEMS = (
    NatureItem("🌳", "Tree", "Look for leaves, bark, and shade."),
    NatureItem("🐦", "Bird", "Listen for a friendly song."),
    NatureItem("🌼", "Flower", "Notice its colours and shape."),
    NatureItem("🦋", "Butterfly", "Watch gentle wings in the sunshine."),
    NatureItem("🌊", "River", "Look for moving water and smooth stones."),
    NatureItem("🌙", "Moon", "Find the moon when the sky is dark."),
)


class NatureExplorer:
    def __init__(self) -> None:
        self.current_index = 0
        self._found: set[int] = set()

    @property
    def current(self) -> NatureItem:
        return NATURE_ITEMS[self.current_index]

    @property
    def is_found(self) -> bool:
        return self.current_index in self._found

    @property
    def found_count(self) -> int:
        return len(self._found)

    def next(self) -> NatureItem:
        self.current_index = (self.current_index + 1) % len(NATURE_ITEMS)
        return self.current

    def previous(self) -> NatureItem:
        self.current_index = (self.current_index - 1) % len(NATURE_ITEMS)
        return self.current

    def mark_found(self) -> bool:
        if self.is_found:
            return False
        self._found.add(self.current_index)
        return True

    def reset(self) -> None:
        self.current_index = 0
        self._found.clear()

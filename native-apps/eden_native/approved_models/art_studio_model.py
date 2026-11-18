"""A small, offline sticker board for Eden Art Studio."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stamp:
    symbol: str
    colour: str


class ArtBoard:
    def __init__(self, limit: int = 24) -> None:
        self.limit = limit
        self.stamps: list[Stamp] = []
        self._undone: list[Stamp] = []

    def add(self, symbol: str, colour: str) -> bool:
        if len(self.stamps) >= self.limit:
            return False
        self.stamps.append(Stamp(symbol, colour))
        self._undone.clear()
        return True

    def undo(self) -> Stamp | None:
        if not self.stamps:
            return None
        stamp = self.stamps.pop()
        self._undone.append(stamp)
        return stamp

    def redo(self) -> Stamp | None:
        if not self._undone or len(self.stamps) >= self.limit:
            return None
        stamp = self._undone.pop()
        self.stamps.append(stamp)
        return stamp

    def clear(self) -> None:
        self.stamps.clear()
        self._undone.clear()

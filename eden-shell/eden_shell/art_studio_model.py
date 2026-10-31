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

    def add(self, symbol: str, colour: str) -> bool:
        if len(self.stamps) >= self.limit:
            return False
        self.stamps.append(Stamp(symbol, colour))
        return True

    def undo(self) -> Stamp | None:
        return self.stamps.pop() if self.stamps else None

    def clear(self) -> None:
        self.stamps.clear()

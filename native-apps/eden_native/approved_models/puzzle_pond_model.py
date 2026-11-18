"""A calm, offline matching-pairs model for Eden Puzzle Pond."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Card:
    index: int
    symbol: str
    revealed: bool = False
    matched: bool = False


class PuzzlePond:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.cards: list[Card] = []
        self.first: int | None = None
        self.second: int | None = None
        self.pairs = 4
        self.restart()

    def restart(self, pairs: int | None = None) -> None:
        if pairs is not None:
            if pairs not in (3, 4, 6):
                raise ValueError("Choose 3, 4 or 6 pairs")
            self.pairs = pairs
        # Draw each round from the full set of available Eden picture cards.
        # Sampling keeps each pair unique while making the set available across games.
        picture_cards = [
            "Fish", "Butterfly", "Flower", "Turtle", "Duck",
            "Bee", "Star", "Sheep", "Cookie", "Owl", "Giraffe",
            "Rocket", "Dolphin", "Penguin", "Mushroom", "Rabbit", "Eden",
        ]
        symbols = self._rng.sample(picture_cards, self.pairs) * 2
        self._rng.shuffle(symbols)
        self.cards = [Card(index, symbol) for index, symbol in enumerate(symbols)]
        self.first = None
        self.second = None

    def choose(self, index: int) -> str:
        card = self.cards[index]
        if card.matched or card.revealed or self.second is not None:
            return "ignored"
        self.cards[index] = Card(card.index, card.symbol, True, False)
        if self.first is None:
            self.first = index
            return "first"
        self.second = index
        if self.cards[self.first].symbol == card.symbol:
            self.cards[self.first] = Card(self.first, self.cards[self.first].symbol, True, True)
            self.cards[index] = Card(index, card.symbol, True, True)
            self.first = None
            self.second = None
            return "matched"
        return "second"

    def finish_mismatch(self) -> None:
        if self.first is None or self.second is None:
            return
        for index in (self.first, self.second):
            card = self.cards[index]
            self.cards[index] = Card(card.index, card.symbol, False, False)
        self.first = None
        self.second = None

    @property
    def complete(self) -> bool:
        return bool(self.cards) and all(card.matched for card in self.cards)

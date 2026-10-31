"""Offline first-letter matching rounds for Eden Word Woodland."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class WordRound:
    symbol: str
    word: str
    answer: str
    choices: tuple[str, ...]


_ROUNDS = (
    ("☀️", "SUN", "S", ("S", "M", "B", "T")),
    ("🐝", "BEE", "B", ("B", "S", "C", "D")),
    ("🌙", "MOON", "M", ("M", "N", "L", "P")),
    ("🐟", "FISH", "F", ("F", "S", "H", "W")),
    ("🌳", "TREE", "T", ("T", "B", "R", "C")),
)


class WordWoodland:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.round: WordRound | None = None

    def new_round(self) -> WordRound:
        symbol, word, answer, choices = self._rng.choice(_ROUNDS)
        shuffled = list(choices)
        self._rng.shuffle(shuffled)
        self.round = WordRound(symbol, word, answer, tuple(shuffled))
        return self.round

    def answer(self, value: str) -> bool:
        if self.round is None:
            raise RuntimeError("start a round before answering")
        return value == self.round.answer

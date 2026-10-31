"""Small, offline counting game logic for Eden Number Meadow."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Round:
    count: int
    choices: tuple[int, ...]


class NumberMeadow:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.round: Round | None = None

    def new_round(self) -> Round:
        count = self._rng.randint(1, 10)
        choices = {count}
        while len(choices) < 4:
            choices.add(self._rng.randint(1, 10))
        values = list(choices)
        self._rng.shuffle(values)
        self.round = Round(count=count, choices=tuple(values))
        return self.round

    def answer(self, value: int) -> bool:
        if self.round is None:
            raise RuntimeError("start a round before answering")
        return value == self.round.count

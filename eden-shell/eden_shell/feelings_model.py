"""Offline feelings check-in and calming actions for Eden."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Feeling:
    key: str
    symbol: str
    label: str


FEELINGS = (
    Feeling("happy", "🙂", "Happy"),
    Feeling("okay", "😐", "Okay"),
    Feeling("worried", "😟", "Worried"),
    Feeling("quiet", "😌", "Quiet"),
)

CALM_ACTIONS = (
    ("🌬️", "Take three slow breaths"),
    ("🧸", "Choose a cosy place"),
    ("🎵", "Listen to a favourite quiet sound"),
)


class FeelingsSpace:
    def __init__(self) -> None:
        self.mood: Feeling | None = None
        self.completed: list[bool] = [False] * len(CALM_ACTIONS)

    def choose_mood(self, key: str) -> bool:
        for feeling in FEELINGS:
            if feeling.key == key:
                self.mood = feeling
                return True
        return False

    def toggle_action(self, index: int) -> bool:
        self.completed[index] = not self.completed[index]
        return self.completed[index]

    @property
    def completed_count(self) -> int:
        return sum(self.completed)

    def reset(self) -> None:
        self.mood = None
        self.completed = [False] * len(CALM_ACTIONS)

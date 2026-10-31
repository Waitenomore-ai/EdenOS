"""A simple, offline visual routine checklist."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoutineStep:
    symbol: str
    label: str


STEPS = (
    RoutineStep("🌞", "Get ready"),
    RoutineStep("🥣", "Eat or drink"),
    RoutineStep("🎒", "Pack what you need"),
    RoutineStep("🌳", "Take a calm break"),
)


class Routine:
    def __init__(self) -> None:
        self.completed: list[bool] = [False] * len(STEPS)

    def toggle(self, index: int) -> bool:
        self.completed[index] = not self.completed[index]
        return self.completed[index]

    def reset(self) -> None:
        self.completed = [False] * len(STEPS)

    @property
    def finished(self) -> bool:
        return all(self.completed)

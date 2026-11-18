"""A simple, offline visual routine checklist."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RoutineStep:
    symbol: str
    label: str


ROUTINES = {
    "full_day": (
        RoutineStep("🌞", "Wake up"), RoutineStep("👕", "Get dressed"),
        RoutineStep("🪥", "Brush my teeth"), RoutineStep("🥣", "Have breakfast"),
        RoutineStep("🎒", "School time"), RoutineStep("⚽", "Play time"),
        RoutineStep("🛁", "Have a bath or wash"), RoutineStep("🌙", "Get cosy and go to bed"),
    ),
    "morning": (
        RoutineStep("🌞", "Wake up"), RoutineStep("🚽", "Use the toilet"),
        RoutineStep("🧼", "Wash my face"), RoutineStep("👕", "Get dressed"),
        RoutineStep("🪥", "Brush my teeth"), RoutineStep("🥣", "Have breakfast"),
        RoutineStep("🎒", "Get my things ready"),
    ),
    "afternoon": (
        RoutineStep("🥪", "Have lunch"), RoutineStep("💧", "Have a drink"),
        RoutineStep("🌳", "Take a calm break"), RoutineStep("🎨", "Play or create"),
        RoutineStep("📚", "Read or learn"), RoutineStep("🍎", "Have a snack"),
        RoutineStep("🧸", "Tidy up"),
    ),
    "after_school": (
        RoutineStep("🏡", "Come home"), RoutineStep("👕", "Get changed"),
        RoutineStep("🍎", "Have a snack"), RoutineStep("📚", "Read or learn"),
        RoutineStep("🎨", "Play or create"), RoutineStep("🧸", "Tidy up"),
        RoutineStep("🌿", "Take a calm break"),
    ),
    "evening": (
        RoutineStep("🍽️", "Have dinner"), RoutineStep("🧸", "Tidy my toys"),
        RoutineStep("🛁", "Have a bath or wash"), RoutineStep("🧸", "Put on pyjamas"),
        RoutineStep("🪥", "Brush my teeth"), RoutineStep("📖", "Story time"),
        RoutineStep("🌙", "Get cosy and go to bed"),
    ),
}
def time_of_day(hour=None):
    hour = datetime.now().hour if hour is None else hour
    return "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"

STEPS = ROUTINES["morning"]


class Routine:
    def __init__(self, steps=None) -> None:
        self.steps = tuple(steps) if steps is not None else STEPS
        self.completed: list[bool] = [False] * len(self.steps)

    def toggle(self, index: int) -> bool:
        self.completed[index] = not self.completed[index]
        return self.completed[index]

    def reset(self) -> None:
        self.completed = [False] * len(self.steps)

    @property
    def finished(self) -> bool:
        return all(self.completed)

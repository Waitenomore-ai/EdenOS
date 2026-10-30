"""Small, predictable navigation state for the Eden home screen."""

from __future__ import annotations

from dataclasses import dataclass

from .catalogue import CATEGORIES


@dataclass
class ScreenState:
    page: str = "home"
    category: str | None = None

    def open_category(self, category: str) -> None:
        if category not in {item.slug for item in CATEGORIES}:
            raise ValueError(f"Unknown Eden activity category: {category}")
        self.page = "category"
        self.category = category

    def open_progress(self) -> None:
        self.page = "progress"
        self.category = None

    def open_help(self) -> None:
        self.page = "help"
        self.category = None

    def open_settings(self) -> None:
        self.page = "settings"
        self.category = None

    def go_home(self) -> None:
        self.page = "home"
        self.category = None

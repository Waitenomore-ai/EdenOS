"""A tiny, deterministic offline picture-story sequence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    symbol: str
    sentence: str


SCENES = (
    Scene("🌱", "A little seed wakes up in the warm earth."),
    Scene("🌧️", "Soft rain gives the seed a drink."),
    Scene("🌼", "A bright flower opens to the sun."),
    Scene("🦋", "A butterfly visits the happy garden."),
)


class StoryGarden:
    def __init__(self) -> None:
        self.position = 0

    @property
    def scene(self) -> Scene:
        return SCENES[self.position]

    @property
    def finished(self) -> bool:
        return self.position == len(SCENES) - 1

    def next_scene(self) -> Scene:
        if not self.finished:
            self.position += 1
        return self.scene

    def restart(self) -> Scene:
        self.position = 0
        return self.scene

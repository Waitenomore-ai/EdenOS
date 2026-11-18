"""A tiny, deterministic offline picture-story sequence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    symbol: str
    sentence: str


SCENES = (
    Scene("🌱", "Once upon a time, a tiny seed lay tucked beneath the warm soil of a beautiful garden. The seed wanted to see the sky, but it did not know how to begin."),
    Scene("🌧️", "One morning, soft rain began to fall. The seed drank the water and felt its little roots stretch into the ground. It was the first step of a wonderful adventure."),
    Scene("☀️", "The next day, the clouds parted and golden sunlight warmed the earth. The seed pushed a tiny green shoot upward until it could feel the sunshine on its leaves."),
    Scene("🐛", "A friendly caterpillar walked past the little shoot. 'Keep growing,' the caterpillar said. 'Every big flower started out small.' The shoot felt brave and proud."),
    Scene("🌼", "After many mornings of rain and sunshine, the little shoot grew into a bright yellow flower. Its petals opened wide, and the garden sparkled with colour."),
    Scene("🦋", "A butterfly landed beside the flower. Together they watched bees buzzing, birds singing and other flowers dancing gently in the breeze."),
    Scene("🌈", "Soon the garden was full of new friends. Each plant grew in its own way, and every flower made the meadow more beautiful."),
    Scene("💚", "As the sun went down, the flower smiled. It remembered the rain, the sunshine and the kindness of its friends. Tomorrow would bring another lovely day in the garden."),
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

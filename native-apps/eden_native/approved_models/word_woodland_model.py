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


_ADVANCED_ROUNDS = (
    ("🐻", "BEAR", "B", ("B", "D", "P", "M")),
    ("🐶", "DOG", "D", ("D", "B", "G", "P")),
    ("🦆", "DUCK", "D", ("D", "T", "B", "C")),
    ("🌸", "FLOWER", "F", ("F", "P", "T", "S")),
    ("🍃", "LEAF", "L", ("L", "I", "T", "F")),
    ("🌧️", "RAIN", "R", ("R", "B", "P", "N")),
    ("🌟", "STAR", "S", ("S", "C", "T", "P")),
    ("🐑", "SHEEP", "S", ("S", "B", "F", "H")),
    ("🍪", "COOKIE", "C", ("C", "K", "B", "D")),
    ("🦉", "OWL", "O", ("O", "A", "U", "E")),
    ("🐸", "FROG", "F", ("F", "V", "P", "T")),
    ("🍎", "APPLE", "A", ("A", "E", "O", "U")),
    ("🐢", "TURTLE", "T", ("T", "D", "P", "C")),
    ("🌈", "RAINBOW", "R", ("R", "B", "W", "N")),
    ("🐱", "CAT", "C", ("C", "K", "S", "T")),
    ("🐘", "ELEPHANT", "E", ("E", "A", "I", "O")),
    ("🦒", "GIRAFFE", "G", ("G", "C", "J", "H")),
    ("🚀", "ROCKET", "R", ("R", "W", "L", "P")),
    ("🐬", "DOLPHIN", "D", ("D", "B", "T", "P")),
    ("🍓", "STRAWBERRY", "S", ("S", "C", "T", "F")),
    ("🌻", "SUNFLOWER", "S", ("S", "F", "C", "T")),
    ("🚲", "BICYCLE", "B", ("B", "D", "P", "R")),
    ("🧩", "PUZZLE", "P", ("P", "B", "R", "T")),
    ("🎨", "PAINT", "P", ("P", "R", "B", "T")),
    ("🐧", "PENGUIN", "P", ("P", "B", "T", "R")),
)

# Curated Eden OS picture vocabulary. Existing words stay unchanged.
_VERIFIED_EXTRA_WORDS = ('ACORN', 'AIRPLANE', 'ANT', 'BALL', 'BIRD', 'BUTTERFLY', 'CAKE', 'CAR', 'CLOUD', 'DRUM', 'EARTH', 'EGG', 'ENVELOPE', 'FEATHER', 'FOX', 'GOOSE', 'GRAPES', 'GUITAR', 'HAT', 'HEART', 'HEDGEHOG', 'HOT AIR BALLOON', 'HOUSE', 'ICE CREAM', 'IGLOO', 'INSECT', 'ISLAND', 'JAM JAR', 'JELLYFISH', 'JET', 'JUICE', 'KANGAROO', 'KEY', 'KITE', 'KOALA', 'LADYBIRD', 'LAMP', 'LION', 'MILK', 'MOUSE', 'MUSHROOM', 'NIGHT SKY', 'NOTEBOOK', 'NUMBERS', 'OCTOPUS', 'ORANGE', 'PEAR', 'PIANO', 'PUMPKIN', 'QUAIL', 'QUESTION MARK', 'RABBIT', 'SNAIL', 'TEDDY', 'TRAIN', 'UMBRELLA', 'UNICORN', 'VASE', 'VEGETABLES', 'VIOLIN', 'VOLCANO', 'WATCH', 'WATERMELON', 'WHALE', 'WORM', 'X RAY FISH', 'XYLOPHONE', 'YACHT', 'YARN', 'YO YO', 'ZEBRA', 'ZIGZAG', 'ZIPPER', 'ZOO')
_EXTRA_ROUNDS = tuple(("🌿", word, word[0], (word[0], *tuple(letter for letter in "BCDFGHLMRSTPAEIOUVWXYZ" if letter != word[0])[:3])) for word in _VERIFIED_EXTRA_WORDS)

class WordWoodland:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.round: WordRound | None = None
        self._previous_word: str | None = None
        self._remaining_words: list[str] = []

    def new_round(self, level: int = 1) -> WordRound:
        if type(level) is not int or not 1 <= level <= 20:
            raise ValueError("Invalid difficulty level")
        # Offer the complete A-Z picture library from the first round.
        pool = _ROUNDS + _ADVANCED_ROUNDS + _EXTRA_ROUNDS
        by_word = {item[1]: item for item in pool}
        if not self._remaining_words:
            self._remaining_words = list(by_word)
            self._rng.shuffle(self._remaining_words)
            if len(self._remaining_words) > 1 and self._remaining_words[-1] == self._previous_word:
                self._remaining_words[0], self._remaining_words[-1] = self._remaining_words[-1], self._remaining_words[0]
        word = self._remaining_words.pop()
        symbol, word, answer, choices = by_word[word]
        self._previous_word = word
        # Increase answer choices without duplicates, preserving the correct letter.
        card_count = {1: 4, 2: 6, 3: 8}.get(level, 8)
        shuffled = [answer]
        for letter in choices:
            if letter not in shuffled:
                shuffled.append(letter)
        distractors = [letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letter not in shuffled]
        self._rng.shuffle(distractors)
        shuffled.extend(distractors[:max(0, card_count - len(shuffled))])
        shuffled = shuffled[:card_count]
        self._rng.shuffle(shuffled)
        self.round = WordRound(symbol, word, answer, tuple(shuffled))
        return self.round

    def answer(self, value: str) -> bool:
        if self.round is None:
            raise RuntimeError("start a round before answering")
        return value == self.round.answer

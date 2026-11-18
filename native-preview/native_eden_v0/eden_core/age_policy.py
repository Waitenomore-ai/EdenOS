from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable

@dataclass(frozen=True)
class ChildAge:
    """An adult supplies either a date of birth or an age, never both."""
    date_of_birth: date | None = None
    age_years: int | None = None

    def __post_init__(self):
        if (self.date_of_birth is None) == (self.age_years is None):
            raise ValueError("Enter a date of birth or an age.")
        if self.age_years is not None and (type(self.age_years) is not int or not 0 <= self.age_years <= 17):
            raise ValueError("Age must be 0–17.")
        if self.date_of_birth is not None and (not isinstance(self.date_of_birth,date) or self.date_of_birth > date.today() or self.date_of_birth.year < date.today().year - 18):
            raise ValueError("Date of birth is outside the child profile range.")

    def age(self, today: date | None = None) -> int:
        if self.age_years is not None:
            return self.age_years
        today = today or date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

@dataclass(frozen=True)
class AgeRating:
    min_age: int
    max_age: int

    def __post_init__(self):
        if type(self.min_age) is not int or type(self.max_age) is not int or not 0 <= self.min_age <= self.max_age <= 17:
            raise ValueError("Invalid age range")

def allowed_for_child(activity_id: str, age: int, ratings: dict[str, AgeRating], allowed_overrides: Iterable[str] = (), blocked_overrides: Iterable[str] = ()) -> bool:
    """Unknown/unrated activities are hidden until an adult reviews them."""
    if activity_id in blocked_overrides:
        return False
    if activity_id in allowed_overrides:
        return True
    rating = ratings.get(activity_id)
    return rating is not None and rating.min_age <= age <= rating.max_age

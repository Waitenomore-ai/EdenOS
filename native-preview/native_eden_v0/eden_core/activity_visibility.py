"""Parent-reviewed activity visibility, separate from public child profile cards."""
from __future__ import annotations
from datetime import date
from .age_policy import AgeRating, ChildAge, allowed_for_child

# All entries must be reviewed and explicitly rated before use.
REVIEWED_RATINGS = {
    "number-meadow": AgeRating(3, 17),
    "word-woodland": AgeRating(4, 17),
    "story-garden": AgeRating(3, 17),
    "art-studio": AgeRating(3, 17),
    "puzzle-pond": AgeRating(3, 17),
    "time-routines": AgeRating(3, 17),
    "nature-explorer": AgeRating(3, 17),
    "find-eden": AgeRating(3, 17),
    "feelings-quiet-space": AgeRating(3, 17),
}

def visible_activities(activities, date_of_birth: str | None,
                       allow=(), block=()):
    """No DOB means no automatic age-based filtering; parent must configure it."""
    if date_of_birth is None:
        return ()
    try:
        age = ChildAge(date_of_birth=date.fromisoformat(date_of_birth)).age()
    except (TypeError, ValueError):
        # Invalid or unconfigured child profiles must not reveal activities.
        return ()
    return tuple(item for item in activities if allowed_for_child(
        item.id, age, REVIEWED_RATINGS, allow, block))

"""Load the local, adult-reviewed Eden activity catalogue."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Category:
    slug: str
    label: str
    icon: str


CATEGORIES = (
    Category("learn", "Learn", "learn"),
    Category("play", "Play", "play"),
    Category("read", "Read", "read"),
    Category("create", "Create", "create"),
)
_CATEGORY_SLUGS = frozenset(category.slug for category in CATEGORIES)
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DESKTOP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.desktop$")


@dataclass(frozen=True)
class Activity:
    id: str
    title: str
    description: str
    category: str
    desktop_id: str
    offline: bool


def _valid_activity(record: Any) -> Activity | None:
    if not isinstance(record, dict) or record.get("reviewed") is not True:
        return None

    activity_id = record.get("id")
    title = record.get("title")
    description = record.get("description")
    category = record.get("category")
    desktop_id = record.get("desktop_id")
    offline = record.get("offline")

    if not isinstance(activity_id, str) or not _SLUG.fullmatch(activity_id):
        return None
    if not isinstance(title, str) or not title.strip() or len(title) > 80:
        return None
    if not isinstance(description, str) or len(description) > 240:
        return None
    if not isinstance(category, str) or category not in _CATEGORY_SLUGS:
        return None
    if not isinstance(desktop_id, str) or not _DESKTOP_ID.fullmatch(desktop_id):
        return None
    if not isinstance(offline, bool):
        return None

    return Activity(
        id=activity_id,
        title=title.strip(),
        description=description.strip(),
        category=category,
        desktop_id=desktop_id,
        offline=offline,
    )


def load_catalogue(path: Path | None = None) -> tuple[Activity, ...]:
    """Return only reviewed local activities; invalid files fail closed."""
    source = path or Path(__file__).parent / "data" / "activities.json"
    try:
        records = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ()
    if not isinstance(records, list):
        return ()

    activities: list[Activity] = []
    seen: set[str] = set()
    for record in records:
        activity = _valid_activity(record)
        if activity is not None and activity.id not in seen:
            activities.append(activity)
            seen.add(activity.id)
    return tuple(activities)

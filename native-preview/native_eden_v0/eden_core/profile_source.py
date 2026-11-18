"""Read-only adapter for the approved iMac's child-card JSON format.

Does not create, migrate, save, or log child accounts.
"""
from __future__ import annotations

import json
from pathlib import Path

from .profile_cards import ProfileCard, make_profile_card


def read_profile_cards(path: Path) -> tuple[ProfileCard, ...]:
    """Return validated local cards or no cards for unsafe/missing input."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        records = document["profiles"]
        if not isinstance(records, list):
            return ()
        cards = tuple(
            make_profile_card(
                record["username"],
                record["display_name"],
                record["avatar"],
                record.get("date_of_birth"),
            )
            for record in records
        )
        if len({card.username for card in cards}) != len(cards):
            return ()
        return cards
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError):
        return ()

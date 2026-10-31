"""Local accessibility preferences for the Eden child session."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AccessibilityPreferences:
    text_scale: float = 1.0
    high_contrast: bool = False
    reduced_motion: bool = False


def accessibility_preset(name: str) -> AccessibilityPreferences:
    """Return a named, safe accessibility starting point."""
    presets = {
        "calm": AccessibilityPreferences(),
        "clear-large": AccessibilityPreferences(1.3, False, True),
        "high-contrast": AccessibilityPreferences(1.2, True, True),
    }
    return presets.get(name, AccessibilityPreferences())


def default_preferences_path() -> Path:
    configured_home = os.environ.get("XDG_CONFIG_HOME")
    config_home = Path(configured_home) if configured_home else Path.home() / ".config"
    return config_home / "eden-os" / "accessibility.json"


def _normalise(raw: Any) -> AccessibilityPreferences:
    if not isinstance(raw, dict):
        return AccessibilityPreferences()

    scale = raw.get("text_scale", 1.0)
    if type(scale) not in (float, int) or not 1.0 <= float(scale) <= 1.6:
        scale = 1.0
    high_contrast = raw.get("high_contrast", False)
    reduced_motion = raw.get("reduced_motion", False)
    if not isinstance(high_contrast, bool):
        high_contrast = False
    if not isinstance(reduced_motion, bool):
        reduced_motion = False

    return AccessibilityPreferences(
        text_scale=float(scale),
        high_contrast=high_contrast,
        reduced_motion=reduced_motion,
    )


def load_preferences(path: Path | None = None) -> AccessibilityPreferences:
    source = path or default_preferences_path()
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return AccessibilityPreferences()
    return _normalise(raw)


def save_preferences(
    preferences: AccessibilityPreferences, path: Path | None = None
) -> None:
    destination = path or default_preferences_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".eden-preferences-", suffix=".json", dir=destination.parent
    )
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(asdict(_normalise(asdict(preferences))), handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


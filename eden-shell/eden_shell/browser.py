"""Fail-closed validation for the system KidsTube browser policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


POLICY_PATH = Path("/etc/firefox/policies/policies.json")
_KIDSTUBE_EXCEPTIONS = {
    "https://kids-tube.com/*",
    "https://www.kids-tube.com/*",
    "https://www.youtube-nocookie.com/embed/*",
    "https://youtube-nocookie.com/embed/*",
    "https://*.ytimg.com/*",
    "https://*.googlevideo.com/*",
}


def kidstube_policy_ready(path: Path = POLICY_PATH) -> bool:
    """Return true only when the restrictive pilot policy is present and valid."""
    try:
        document: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(document, dict):
        return False
    policies = document.get("policies")
    if not isinstance(policies, dict):
        return False

    website_filter = policies.get("WebsiteFilter")
    if not isinstance(website_filter, dict):
        return False
    if website_filter.get("Block") != ["<all_urls>"]:
        return False
    exceptions = website_filter.get("Exceptions")
    if (
        not isinstance(exceptions, list)
        or any(not isinstance(item, str) for item in exceptions)
        or set(exceptions) != _KIDSTUBE_EXCEPTIONS
    ):
        return False

    required_flags = (
        "BlockAboutAddons",
        "BlockAboutConfig",
        "BlockAboutProfiles",
        "BlockAboutSupport",
        "DisableDeveloperTools",
        "DisableFirefoxAccounts",
        "DisableFirefoxStudies",
        "DisablePrivateBrowsing",
        "DisableTelemetry",
        "SanitizeOnShutdown",
    )
    if any(policies.get(flag) is not True for flag in required_flags):
        return False
    homepage = policies.get("Homepage")
    return (
        isinstance(homepage, dict)
        and homepage.get("URL") == "https://www.kids-tube.com/"
        and homepage.get("StartPage") == "homepage-locked"
        and homepage.get("Locked") is True
    )

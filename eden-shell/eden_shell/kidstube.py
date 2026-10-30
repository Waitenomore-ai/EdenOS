"""Launch KidsTube in Firefox only when its deny-by-default policy is valid."""

from __future__ import annotations

import os
import sys

from .browser import browser_access_ready


def main() -> int:
    if not browser_access_ready():
        print("KidsTube is unavailable: the browser policy is missing or invalid.", file=sys.stderr)
        return 1
    os.execv(
        "/usr/bin/firefox-esr",
        [
            "/usr/bin/firefox-esr",
            "--new-window",
            "https://www.kids-tube.com/",
        ],
    )
    return 1  # pragma: no cover - execv replaces this process on success


if __name__ == "__main__":
    raise SystemExit(main())


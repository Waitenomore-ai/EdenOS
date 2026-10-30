"""Suppress accidental rapid repeat activity launches on the GTK main thread."""
from time import monotonic


class LaunchCooldown:
    def __init__(self, clock=monotonic):
        self._clock = clock
        self._started = {}

    def try_start(self, activity_id: str) -> bool:
        now = self._clock()
        previous = self._started.get(activity_id)
        if previous is not None and now - previous < 2.0:
            return False
        self._started[activity_id] = now
        return True

    def release(self, activity_id: str) -> None:
        self._started.pop(activity_id, None)

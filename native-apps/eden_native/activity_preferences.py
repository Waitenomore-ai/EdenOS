"""Per-child activity preferences for the native prototype.

These are launcher preferences, not an OS security boundary.
Writes require a verified ParentSession.
"""
from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from .parent_session import ParentSession
from .profiles import ProfileRepository

ACTIVITIES = ("number-meadow", "word-woodland", "puzzle-pond", "art-studio",
              "nature-explorer", "my-day", "feelings", "story-garden")

class ActivityPreferences:
    def __init__(self, session: ParentSession, profiles: ProfileRepository):
        self.session, self.profiles = session, profiles
        self.root = profiles.path.parent / "activity-choices"

    def _path(self, username):
        if not isinstance(username,str) or self.profiles.get(username) is None:
            raise ValueError("Unknown child")
        return self.root / (username + ".json")

    def load(self, username):
        path = self._path(username)
        if path.is_symlink(): return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("version") != 1 or not isinstance(data.get("enabled"),dict):
                return {}
            return {key:value for key,value in data["enabled"].items()
                    if key in ACTIVITIES and type(value) is bool}
        except (OSError, ValueError, TypeError):
            return {}

    def save(self, username, choices):
        self.session.require_parent()
        if not isinstance(choices,dict) or any(
            key not in ACTIVITIES or type(value) is not bool for key,value in choices.items()
        ):
            raise ValueError("Invalid activity choices")
        path = self._path(username)
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        if path.is_symlink(): raise ValueError("Unsafe activity choices path")
        fd,tmp = tempfile.mkstemp(prefix=".eden-activities-",dir=self.root)
        try:
            os.fchmod(fd,0o600)
            with os.fdopen(fd,"w",encoding="utf-8") as out:
                json.dump({"version":1,"enabled":choices},out,sort_keys=True)
                out.flush();os.fsync(out.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)

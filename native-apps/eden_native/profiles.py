"""Native child profile metadata adapter, using unmodified approved iMac model."""
from pathlib import Path
from .core import DesktopPlatform
from .approved_models.profile_cards import make_profile_card, SELECTABLE_AVATARS
from .approved_models.profile_store import load_profiles, save_profiles

class ProfileRepository:
    def __init__(self, platform: DesktopPlatform):
        self.path = platform.data_root / "profiles.json"

    def all(self):
        return load_profiles(self.path)

    def create(self, username: str, display_name: str, avatar: str):
        profile = make_profile_card(username, display_name, avatar)
        existing = list(self.all())
        if any(p.username == username for p in existing):
            raise ValueError("A child with that username already exists")
        existing.append(profile)
        save_profiles(existing, self.path)
        return profile

    def get(self, username):
        return next((p for p in self.all() if p.username == username), None)

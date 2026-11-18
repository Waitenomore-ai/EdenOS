"""Parent-authorised profile creation service, no GUI bypass."""
from .parent_session import ParentSession
from .profiles import ProfileRepository

class ParentProfileService:
    def __init__(self, session: ParentSession, profiles: ProfileRepository):
        self.session = session
        self.profiles = profiles

    def create(self, username, display_name, avatar):
        self.session.require_parent()
        return self.profiles.create(username, display_name, avatar)

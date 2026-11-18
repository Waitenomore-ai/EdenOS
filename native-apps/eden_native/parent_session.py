"""Parent Corner authentication boundary; PIN validation is injected from approved iMac model."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .core import NavigationState

@dataclass
class ParentSession:
    state: NavigationState
    verify_pin: Callable[[str], bool]

    def authenticate(self, pin: str) -> bool:
        if self.state.page != "parent":
            return False
        if not isinstance(pin, str):
            return False
        accepted = self.verify_pin(pin)
        self.state = self.state.unlock_parent(accepted)
        return accepted

    def change_child(self, child_id: str) -> None:
        self.state = self.state.select_child(child_id)

    def logout(self) -> None:
        self.state = self.state.logout()

    def require_parent(self) -> None:
        if not self.state.parent_unlocked or self.state.page != "parent":
            raise PermissionError("Parent Corner must be unlocked")

    def save_parent_setting(self, operation: Callable[[], None]) -> None:
        self.require_parent()
        operation()

"""Portable Eden desktop core: no GTK/Qt or filesystem side effects."""
from dataclasses import dataclass
from pathlib import Path
import os, sys

@dataclass(frozen=True)
class DesktopPlatform:
    name: str
    config_root: Path
    data_root: Path
    cache_root: Path
    supports_system_wallpaper: bool = False
    supports_kiosk: bool = False

def detect_platform(system=None, home=None, environ=None):
    system = system or sys.platform
    env = dict(os.environ if environ is None else environ)
    home = Path.home() if home is None else Path(home)
    if system.startswith("linux"):
        return DesktopPlatform("linux", Path(env.get("XDG_CONFIG_HOME", home/".config"))/"eden-os", Path(env.get("XDG_DATA_HOME", home/".local/share"))/"eden-os", Path(env.get("XDG_CACHE_HOME", home/".cache"))/"eden-os", True, True)
    if system == "win32":
        config = Path(env.get("APPDATA", home/"AppData/Roaming"))/"EdenOS"
        data = Path(env.get("LOCALAPPDATA", home/"AppData/Local"))/"EdenOS"
        return DesktopPlatform("windows", config, data, data/"Cache")
    if system == "darwin":
        root = home/"Library/Application Support/EdenOS"
        return DesktopPlatform("macos", root, root, home/"Library/Caches/EdenOS")
    raise RuntimeError("Unsupported platform: "+system)

@dataclass(frozen=True)
class NavigationState:
    page: str = "login"
    child_id: str | None = None
    parent_unlocked: bool = False

    def select_child(self, child_id):
        if not isinstance(child_id,str) or not child_id or "/" in child_id or ".." in child_id:
            raise ValueError("Invalid child identifier")
        return NavigationState(page="home", child_id=child_id)

    def open_parent(self):
        return NavigationState(page="parent", child_id=self.child_id)

    def unlock_parent(self, verified):
        if self.page != "parent" or not verified:
            return self
        return NavigationState(page="parent", child_id=self.child_id, parent_unlocked=True)

    def logout(self):
        return NavigationState()

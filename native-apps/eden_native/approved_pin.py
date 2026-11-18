"""Load the approved iMac parent PIN implementation in an isolated native app config."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from .core import DesktopPlatform

class ApprovedPinAdapter:
    def __init__(self, platform: DesktopPlatform, source: Path):
        self.platform = platform
        self.source = Path(source)
        if not self.source.is_file():
            raise FileNotFoundError("Approved PIN model is missing")
        spec = importlib.util.spec_from_file_location("eden_native_approved_parent_pin", self.source)
        self.model = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.model)

        # This adapter owns a unique imported module instance and its path override.
        self.model._path = lambda: self.platform.config_root / "parent-pin.json"

    def has_pin(self):
        return self.model.has_pin()

    def verify_pin(self, pin):
        return self.model.verify_pin(pin)

    def set_pin(self, pin):
        return self.model.set_pin(pin)

"""Development-only screenshot helper; never writes live profiles."""
import os
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication
from eden_native.qt_app import create_window
from eden_native.core import NavigationState, detect_platform
from eden_native.profiles import ProfileRepository
from eden_native.approved_pin import ApprovedPinAdapter

def render():
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as folder:
        platform = detect_platform("linux", Path(folder), {"XDG_DATA_HOME": folder + "/data", "XDG_CONFIG_HOME": folder + "/config"})
        profiles = ProfileRepository(platform)
        profiles.create("eden", "Eden", "approved-eden")
        pin_source = Path(__file__).parent.parent / "eden_native" / "approved_models" / "parent_pin.py"
        pin = ApprovedPinAdapter(platform, pin_source)
        pin.set_pin("2468")
        window = create_window(pin_adapter=pin, profiles=profiles)
        window.resize(1920, 1080)
        window.show()
        app.processEvents()
        for page in ("play", "learn", "story-garden", "art-studio"):
            window.transition(NavigationState(page=page, child_id="eden"))
            app.processEvents()
            out = Path(os.environ.get("EDEN_QA_OUTPUT", folder)) / (page + "-1920x1080.png")
            out.parent.mkdir(parents=True, exist_ok=True)
            window.grab().save(str(out))
            print(out, out.stat().st_size)
        window.close()

if __name__ == "__main__":
    render()

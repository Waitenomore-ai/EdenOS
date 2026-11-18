"""Entry point for isolated Eden Native development previews."""
import os
import sys
from pathlib import Path

# Never point the demonstration build at real Eden OS profile/PIN settings.
os.environ["XDG_CONFIG_HOME"] = str(Path.home() / ".config" / "eden-native-preview-demo")

from native_eden_v0.window import main

def smoke_test():
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    from native_eden_v0.window import EdenNativeWindow
    from native_eden_v0.eden_core.garden_stars import CATALOGUE
    app = QApplication([])
    window = EdenNativeWindow()
    window.show()
    app.processEvents()
    assert window.character_count() == 11
    assert len(CATALOGUE) == 75
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    print("NATIVE_SMOKE_OK: 11 portraits, 75 stickers", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(smoke_test() if "--smoke-test" in sys.argv else main())

"""Isolated Eden Native development preview entrypoint; never touches live Eden OS settings."""
from eden_native.qt_app import main


def smoke_test():
    """Launch the packaged Qt shell without touching real Eden profiles or PINs."""
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    from eden_native.qt_app import create_window
    app = QApplication.instance() or QApplication([])
    window = create_window()
    try:
        window.show()
        app.processEvents()
        assert window.windowTitle().startswith("Eden OS")
        assert window.title.text()
        print("NATIVE_STAGING_SMOKE_OK", flush=True)
        return 0
    finally:
        window.close()
        window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()


if __name__ == '__main__':
    import sys
    raise SystemExit(smoke_test() if "--smoke-test" in sys.argv else main())

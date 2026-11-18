"""Isolated Eden Native development preview entrypoint; never touches live Eden OS settings."""
from eden_native.qt_app import main
if __name__ == '__main__':
    raise SystemExit(main())

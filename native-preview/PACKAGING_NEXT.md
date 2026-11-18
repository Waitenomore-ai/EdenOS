# Windows and macOS build preparation

The Linux source preview provides the cross-platform PySide6 window and a reduced, privacy-safe set of Mac domain models. Executables must be built **on their target operating systems**.

## Windows (not yet built)

- Use Windows Python 3.12 or later on an isolated build machine.
- Create a virtual environment, install requirements.txt.
- Launch with `python -m native_eden_v0.window`.
- Run unit tests and check DPI scaling, keyboard access, portraits, PIN lock, relock and close/reopen.
- Then prepare a platform-specific signed installer; verify publisher, no hidden real profile files, and no auto-start.

## macOS (not yet built)

- Use a supported macOS build machine matching intended architecture.
- Create a virtual environment and install requirements.txt.
- Launch with `python3 -m native_eden_v0.window`.
- Check native window behaviour, accessibility, Retina scaling, app bundle signing/notarisation prerequisites, and clean uninstall.
- Build/test both Apple Silicon and Intel where supported.

## Shared release gates

- Mac design/model remains source of truth.
- Keep demo state separate from production profiles.
- Parent Corner must be locked at launch and after Home.
- No real child data may ship.
- Verify all 11 portraits and 75 approved sticker catalogue entries.
- Stress-test window lifetime before producing installable binaries.
- Obtain Chris's explicit approval before live deployment or website synchronisation.

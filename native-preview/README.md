# Eden Native Linux — Development Preview 0.1.0

This is a Python/PySide6 **native desktop window** prototype, not a production Eden OS installer. It uses eleven demonstration profiles and selected approved avatar images, with copied Mac domain-model modules. No real child profiles, balances, purchases, or settings are included.

## Linux setup

From this folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run-eden.sh
```

Parent Corner starts locked. To configure a **demo-only** PIN, use:

```bash
XDG_CONFIG_HOME="$PWD/demo-config" .venv/bin/python -c 'from native_eden_v0.eden_core.parent_pin import set_pin; import getpass; set_pin(getpass.getpass("New demo PIN (4-8 digits): "))'
```

Run tests:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest native_eden_v0.test_window -q
```

Parent Corner is a convenience in-app PIN gate, **not** an operating-system security boundary. Child Profiles, Activity Controls, Learning Progress, Garden Stars, and Security are read-only prototype views. Demo data must never be confused with real child records.

This package is intentionally not auto-started or installed into Eden's live iMac. Do not copy it into /usr/share/eden-os without a separately approved deployment, rollback backup, and further validation.

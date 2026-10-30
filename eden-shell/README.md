# Eden OS child home screen prototype

This is an early GTK 4 launcher prototype for Debian 13. It has predictable Learn / Play / Read / Create navigation, private progress messaging, adult-help guidance, and locally saved text-size, high-contrast, and reduced-motion preferences. Tux Paint is the first reviewed offline activity.

## Debian runtime packages

Install `python3`, `python3-gi`, `gir1.2-gtk-4.0`, `adwaita-icon-theme`, `librsvg2-common`, and `firefox-esr`. These package names are available in Debian 13 Trixie. The full OS package list and Firefox policy are maintained at the project root.

## Run on a Debian desktop

```sh
PYTHONPATH=. python3 -m eden_shell.app
```

The screen is full-screen by default. Pressing the visible Home button returns from any child-facing page. The separate adult setup app creates local standard accounts; this child shell does not create accounts or record progress. The KidsTube shortcut opens a normal Firefox window only when the system allowlist validates. The activity catalogue only exposes software reviewed in `docs/activities.md` and included in the image.

## Checks

From the `eden-shell` directory:

```sh
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

The model tests use only Python’s standard library. A Debian 13 graphical session is still needed to inspect the GTK layout, keyboard focus, screen-reader labels, and touch behavior.

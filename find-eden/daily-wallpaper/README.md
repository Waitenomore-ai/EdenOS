# Find Eden daily wallpapers — Debian 13 / XFCE

This installer is for the logged-in Eden OS user on the intended computer. It does not require sudo. Nothing is activated merely by unpacking this pack. Python 3 and XFCE's `xfconf-query` must already be installed.

From the extracted `find-eden` directory, preview today's choice without any changes:

```sh
python3 daily-wallpaper/rotator.py --dry-run
```

Install **on the Eden OS computer, in its XFCE desktop terminal**:

```sh
python3 daily-wallpaper/install.py
```

The installer copies the manifest, all listed images, and scripts into `~/.local/share/find-eden` (or `$XDG_DATA_HOME/find-eden`). The extracted source may then be moved or deleted. Existing installations are preserved: uninstall before reinstalling. To prepare startup files without starting anything now, add `--no-start`. The normal installer also enables the optional user timer when a graphical session is available; no-start defers the watcher to the next XFCE login.

The XDG autostart watcher runs within the current login session. It checks the local date every 60 seconds, including after suspend. A daily systemd user timer queues a refresh; only the session watcher performs that request, so a systemd manager with old display/session variables cannot target another desktop. The watcher also works if systemd user timers are unavailable. Duplicate watchers exit using a file lock. Timer and watcher updates are serialized. The watcher requires an identified XFCE session and exits without desktop changes if it cannot find one. It stops when that session exits; login reapplies today's wallpaper, including newly discovered monitors/workspaces.

The selection follows manifest order, starting at the first entry on October 31, 2026, wrapping after the last image. It uses your computer's local calendar date. Invoking it repeatedly on the same day selects the same image; missed days catch up immediately rather than advancing one image at a time. All listed images must be present and valid paths before any change occurs. Dates before the epoch also wrap deterministically.

Every existing XFCE `/backdrop/.../last-image` and `/backdrop/.../image-path` property receives the selected image. Existing sibling `image-style` properties become `4` (scaled/fit), keeping the complete hide-and-seek scene visible. Other settings are untouched. Every original value is backed up before writes; success state is committed atomically only after all writes succeed. A failed update retries within 60 seconds. If XFCE itself fails partway through an update, some wallpaper properties may already have changed; the backup remains available for restore.

Uninstall from the Eden OS XFCE terminal:

```sh
python3 "$HOME/.local/share/find-eden/daily-wallpaper/install.py" --uninstall
```

If you set `XDG_DATA_HOME`, substitute its `find-eden/daily-wallpaper/install.py` path. This blocks further wallpaper updates under the update lock, stops the timer and every verified owned watcher, waits for those processes to exit, restores original wallpaper/style values where properties still exist, and removes only this installation and its autostart/unit files. The stop flag remains until a fresh install; delayed updates cannot reapply removed image paths. If restoring fails, uninstall returns an error and keeps installed images and startup files; log into XFCE and retry. Uninstall refuses directories without a valid installation ownership marker. A fresh reinstall archives previous backup/state files under a `recovery-*` directory, so its next update captures the current wallpaper. The backup remains at `~/.local/state/find-eden/backup.json` (or `$XDG_STATE_HOME/find-eden/backup.json`). Uninstall outside XFCE may be unable to restore; run `rotator.py --restore` from a retained extracted pack after logging into XFCE. The same state directory is used. `--uninstall --no-start` removes files without interacting with systemd or the desktop; log out first if a watcher was already running.

Verification:

```sh
cd daily-wallpaper
python3 -m unittest -v
```

Tests use a temporary home and injected XFCE subprocess boundary. No native desktop was available in the build environment, so actual XFCE autostart/timer activation must be checked on Eden OS. All 28 scenes also have visually mapped hit regions in the bundled game. Browser tests verify source interactions using deterministic artwork fixtures; the real PNG assets are validated separately. Native XFCE activation remains to be tested on the iMac.

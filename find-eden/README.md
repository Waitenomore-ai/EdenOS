# Find Eden! — 28 gardens and daily wallpaper

This pack contains the three original Find Eden scenes, **25 additional wallpapers**, an offline hide-and-seek game, and an optional daily desktop wallpaper changer for Eden OS.

## Play

Extract the whole ZIP and open **Find-Eden.html**. Keep its folders beside it: the game reads its full-resolution images locally, so it does not need to load all 28 pictures into memory at once. There is no server, internet connection, account, timer or saved progress.

Find the little blonde girl in each picture and click or tap her. Ask for a text hint, reveal her hiding place, enlarge the picture, or choose a named place instead of pointing precisely. Keyboard players can focus the scene, move the search ring with arrow keys, and press Enter or Space. Shift plus an arrow makes smaller movements. Optional Listen uses an installed local English voice only; if no voice is available the game explains this. High contrast is available for the controls.

**Today's garden** selects the same scene as the daily wallpaper changer, using the computer's local date. The 28-day sequence begins with Sunrise Garden on 31 October 2026 and repeats after 28 days. The game opens at the first scene initially; use Today's garden to jump to the daily scene.

## Set a new Eden OS desktop wallpaper each day

On the intended Eden OS computer, log into its XFCE desktop. From this extracted folder run:

```sh
python3 daily-wallpaper/install.py
```

No sudo is required. It installs an offline per-user changer, checks the date at login and while the session is open, and selects a different image each day. Restarting in the same day keeps that day's image. Turning the computer off for several days catches up to the correct date on the next login. The full image is fitted to each detected monitor/workspace, so Eden stays in the picture. Existing wallpaper and fit settings are backed up for uninstall.

For a preview that makes no changes:

```sh
python3 daily-wallpaper/rotator.py --dry-run
```

See **daily-wallpaper/README.md** for installation, restoration and removal details. Nothing is activated by unpacking this ZIP. This package was prepared remotely; installation and graphical activation on the iMac are still outstanding. It changes the XFCE desktop background after login. It does not change the boot splash, login greeter, startup music or the appearance of a full-screen application covering the desktop. The static wallpaper is a visual search game; detecting clicks works inside Find-Eden.html.

A browser with an organisation policy blocking local files may not open the game. Do not weaken Eden's existing browser policy to work around that; its dedicated native activity-window integration can be added separately.

## Contents and checks

- `wallpapers/`: the first three PNG scenes.
- `daily-wallpapers/`: 25 new PNG scenes, each 1672 × 941 pixels, approximately 16:9, preserved at generated resolution.
- `wallpapers.json`: daily sequence and image checksums.
- `src/`: game source, verified scene dimensions, hit regions and hints.
- `daily-wallpaper/`: installer, rotator, documentation and tests.

All 28 PNGs were decoded and verified, and their hashes are recorded. Browser checks exercise all 28 scene paths/hit maps, wrong and correct taps, hints, keyboard, picture choices, mobile zoom, replay, today's scene and zero network requests using full-dimension local PNG fixtures. The actual wallpaper pixels were visually inspected and their hit regions mapped separately. Daily changer tests cover dates, repeat calls, missing/invalid manifests, XFCE command failures, session lifetime, installation, restoration and uninstall races. Native XFCE/iMac behavior remains to be checked there.

To rebuild the small HTML file from source, run `python3 build.py` with Pillow installed. `python3 build.py --embed` instead creates a much larger standalone HTML containing every image. Both use the same game source.

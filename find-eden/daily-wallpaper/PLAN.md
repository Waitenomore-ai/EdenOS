# Eden daily wallpaper expansion

Approved request: 25 additional wallpapers with the same blonde girl hiding, plus a new Eden OS wallpaper every day.

Generate 25 original 16:9 scenes, preserving existing files and using the approved character design. Package all 28 scenes. Daily selection is deterministic by local calendar date, cycles without immediate repeats, and does not advance twice in one day. Install a per-user XFCE wallpaper updater, a daily systemd user timer and an XDG login fallback. Validate paths, prefer the active user's session, update all detected XFCE monitor/workspace wallpaper properties, use subprocess argument lists, and do not touch disks, boot, startup music, browser policy or other user settings. Provide uninstall instructions.

Native iMac activation requires that machine; prepare and verify the source and installation package remotely without claiming it is active there. Tests cover repeat invocation, date rollover, reboot catch-up, cycle wrap, missing images, malformed manifests, failed XFCE commands and filenames containing spaces. Keep standalone Find Eden game and its three verified click maps intact; new artwork has manually checked hit regions and the game includes all 28 scenes.

Verification complete: 13 Python tests pass, including restore/reinstall/ownership/session/uninstall races. XFCE fit mode corrected to SCALED=4 after checking upstream enum and renderer source. Native activation on the iMac remains outstanding.

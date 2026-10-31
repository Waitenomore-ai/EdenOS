# Find Eden in the next ISO and installed-system update

The source includes the complete 28-scene wallpaper/game pack. Both ISO staging and the Debian update builder validate the manifest, dimensions and all PNG checksums, then copy the offline runtime into `/usr/share/eden-os/find-eden`. The built ISO workflow verifies all 28 wallpaper hashes inside its actual squashfs.

Find Eden is in Play and the desktop applications menu. Its dedicated GTK4/WebKit6 window opens bundled files only, starts at today’s garden, and does not change Firefox/KidsTube policy. WebKit6 is part of the ISO/update dependencies. The child home screen shows the daily garden because the child session itself does not run xfdesktop.

Full XFCE sessions start the daily wallpaper watcher automatically with their current session environment. Wallpaper date selection and the game use the same 28-day sequence. Shared images do not need to be copied separately into every child profile. Existing boot branding, startup music and login settings are preserved. User wallpaper state is written under XDG_STATE_HOME and not shipped inside the update.

Native iMac display, sound and boot validation still require testing on the hardware. Adding this source does not claim a new ISO has already been built.

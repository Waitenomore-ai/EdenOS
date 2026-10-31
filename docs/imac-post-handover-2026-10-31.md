# iMac follow-up after 31 October 2026 handover

## Verified on the live pilot
- Installed `eden-os-desktop` package reports `install ok installed`.
- Wireless AR928X using `ath9k` is connected to **The Waites** over `wlp3s0`.
- SSH access using the dedicated key works over Wi-Fi.
- Six Garden wallpapers and the Eden logo are on disk; the launcher loads a plain CSS background in the earlier package.
- Adult `edenadmin` uses XFCE by design. The Eden Child Session is a separate selectable login session.

## Changes proposed in this branch
- Adult installed package excludes `/etc/plymouth/plymouthd.conf`, which Debian's `plymouth` package owns. This avoids a failed dpkg overwrite, while leaving existing configuration untouched.
- Adds `wpasupplicant` as a package dependency so NetworkManager can operate Wi-Fi without a separate manual install.
- Uses the shipped sunrise garden wallpaper in the Eden GTK launcher, with a pale translucent content panel and a solid high-contrast override.

## Validation before deployment
1. Build the Debian package and check it contains **no** `etc/plymouth/plymouthd.conf` or corresponding conffile entry.
2. Test GTK CSS parsing and visually review at 1024x768 and 1920x1080, including text scaling, reduced motion and high-contrast mode.
3. Simulate `apt install` on a clean disposable Debian 13 VM; test a real upgrade and rollback procedure there.
4. Confirm network-manager + wpasupplicant on a clean image.
5. Only then offer a new signed/verified package for the Kingston SSD, preserving the adult XFCE and the known-working basic-graphics entry.

The iMac remains a development target. Avoid switching the adult account to a child/kiosk session or rebooting remotely without an onsite recovery route.

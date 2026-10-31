# Update an installed EdenOS iMac

An ISO is primarily installation and live-test media. It does not automatically
update an existing installation. Use the `eden-os-desktop` Debian package to
update the launcher, setup, session files and managed defaults without replacing
accounts, home folders, partitions or the bootloader.

This is the first development update package, not a fully tested stable update
service. Back up important child work before the first installed-system trial.
Normal Radeon graphics on the pilot iMac still needs diagnosis. Continue choosing
the working basic-graphics boot entry; this package deliberately makes no GRUB or
kernel-argument changes.

## Adult installation

1. On the iMac, boot basic graphics and log in as `edenadmin`.
2. Download the update artifact for the intended source revision from the
   repository's **Build EdenOS installed-system update** workflow. Extract the
   artifact ZIP; keep the `.deb` and `eden-os-update.sha256` together. A build's
   ISO artifact also includes the update package from the same source.
3. Open a terminal in that extracted folder and verify its checksum:

   ```sh
   sha256sum -c eden-os-update.sha256
   ```

4. Check that the matching Debian firmware repository is enabled:

   ```sh
   cat /etc/apt/sources.list
   ```

   The pilot installation uses ordinary `deb` lines ending in
   `main non-free-firmware`. If that component is absent, add it to those lines
   with the adult's editor. Do not apply this instruction to an unrelated server.
   Debian's `.sources` format uses `Components: main non-free-firmware` instead.

5. Refresh package indexes, then install the exact downloaded filename:

   ```sh
   sudo apt update
   sudo apt install ./eden-os-desktop_VERSION_all.deb
   ```

   Replace `VERSION` with the filename shown in the folder. Review apt's proposed
   changes. If dependencies cannot be resolved, stop rather than forcing dpkg.
   The package uses standard Debian conffile handling for its `/etc` defaults;
   retain local settings when asked unless deliberately changing that policy.
6. Log out and back in to use updated session files. A running launcher continues
   using its old process until closed. Existing users can find **Eden Home** in
   the Education menu and **Eden Adult Setup** in Settings, or run `eden-shell`
   and `eden-setup`. Desktop shortcuts from `/etc/skel` apply only to new users.
7. Verify launcher opening, Tux Paint launching, adult setup and child login.
   Do not mark the update accepted based only on an apt success message.

Firmware dependencies may regenerate initramfs through Debian's package hooks.
Do not power off during installation. Avoid restarting until apt has finished.
The update does not activate third-party candidate apps, change browser policy
to enabled, create accounts or start recording child progress.

## Verify and recover

```sh
dpkg-query -W eden-os-desktop
cat /usr/share/eden-os/update.json
eden-system-report
```

Keep the previous package and a backup. Installing an earlier package requires
reviewing its dependencies and conffile changes; it is not a full system restore.
If graphical startup fails, select basic graphics at boot. If apt was interrupted,
inspect its error before attempting `sudo dpkg --configure -a`.

## Build and delivery

The update workflow tests real GTK construction and builds the package in Debian
13. Every artifact includes a SHA-256 checksum. GitHub artifact access is used for
development delivery; this is not an unattended or signed apt repository.
No iMac has yet accepted this new package in a physical update test.

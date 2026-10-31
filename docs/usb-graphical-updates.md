# Eden OS graphical USB updater (development)

The adult-only **Eden OS Updates** app supports a future ISO that includes an update payload under `/eden-update/`. It does not run the Debian installer, partition disks, modify GRUB, or erase accounts.

## Build and deliver

The ISO build copies `eden-os-desktop_VERSION_all.deb` and `eden-os-update.sha256` into the ISO at `/eden-update/`, while keeping the normal downloadable update package alongside the ISO.

On the installed iMac, boot the existing installation using the known-working basic-graphics option. Log in as the adult administrator. Plug in the USB and mount it; open **Eden OS Updates** from Settings. Select the ISO file on the USB stick, or select a directory containing the matching .deb and .sha256 files (paste its path into the box). Click **Check and verify update**. A package checksum mismatch, wrong package name, absent ISO payload or downgrade prevents installation.

Before installing, back up child-created work. Click **Review installation in terminal**; authenticate as administrator and **read apt's proposed changes before confirming**. Cancel if apt proposes removing important packages or if the dependency plan looks wrong. Log out and log back in after the update.

A USB that was written directly from an ISO typically exposes the mounted ISO's file tree, **not the original ISO file**. On such sticks, locate the `eden-update` folder and enter its path instead. Ventoy sticks store the ISO as a file, so ISO selection works directly.

## Limitations and safety

- This is a development candidate, not a tested physical iMac upgrade. It has not been run on the actual Kingston SSD.
- A standalone older ISO without `/eden-update/` cannot update the installation. Use its separately downloaded .deb and checksum from the corresponding GitHub Actions artifact.
- SHA-256 catches accidental damage but **does not authenticate a malicious replacement ISO**. Only use media built from a trusted Eden OS source/workflow; compare the ISO checksum with a trustworthy published checksum.
- Installation uses Debian's apt transaction; **not** disk cloning, a snapshot rollback, offline transactional update or a guaranteed recovery mechanism.
- The installer/live environment is never used for an in-place update.
- Adult authentication, reliable backups, rollback and power-loss recovery require physical testing before general release.
- If xorriso is unavailable, install it in the adult environment or use the extracted `.deb` and checksum folder.
- GTK4/PyGObject and an interactive terminal are required. Do not run this from a child session.

## Test gate

Test using a disposable Debian 13 VM first: inspect ISO with xorriso, check verification failure on corruption/absent checksum/older version, inspect apt dependency prompt, then run a successful upgrade and reboot. Repeat on the iMac only after backing up the Kingston SSD. Do not describe this workflow as production-ready based on source review alone.

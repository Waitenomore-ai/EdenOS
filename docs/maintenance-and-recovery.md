# Adult maintenance and recovery — development procedure

These steps are for an adult administrator. Test them on a disposable installed
EdenOS system before depending on them; interrupted-update recovery and automatic
rollback are not implemented.

## Identify and measure

Run `eden-system-report` in the adult terminal. It prints local JSON containing
build identity, CPU, model, firmware width, physical memory, and root filesystem
capacity/free space. It does not collect serial numbers, usernames or hostnames,
and does not upload anything. Firmware width can be unknown on a legacy boot.

`within_budget` is a conservative root-filesystem check (total minus free at
most 20 GiB, free at least 6 GiB), not proof of a 32 GB device or installed image
size. Collect it after installation and updates; live-session overlay figures
are not installation measurements.

## Security updates

1. Sign into the adult desktop and save/close activities.
2. Make a verified backup of important work, connect power and check free space.
3. Open Software Updates if available, or run `sudo apt update` then
   `sudo apt upgrade` in the adult terminal. Read the proposed changes and stop
   on errors or unexpected removals. Do not use unattended full-upgrade here.
4. Restart if required, then verify adult login, child login, offline activity
   launch and saved work. Record the new package state and available space.
5. If an update fails, preserve the error message and use the adult account for
   diagnosis. This prototype has no guaranteed one-click rollback.

## Children’s work backup and restore

For a quick backup of the current adult or child home, create or connect an
existing writable destination directory and run:

```sh
eden-backup /path/to/external/backup-folder
```

The command creates a new private timestamped archive and never overwrites an
existing archive. It includes common Eden work folders and `.config/eden-os`,
but excludes `.cache`. It is a convenience backup, not a full disk image; open
sample files from the archive before treating it as verified.

1. Have each child save and close their activities; sign them out.
2. In the adult desktop, copy the selected child's personal work directories
   to adult-managed external storage. Check the app's actual save directory;
   do not assume every app uses Documents or Pictures.
3. Include hidden app data only when needed for saved work. Do not restore
   system files, login/session configuration or browser policies from backups.
4. Confirm the destination device and available space before copying. A backup
   is verified only after opening sample saved files from the copy.
5. Rehearse restoring into a disposable child account. Copy personal files
   back using adult tools and set ownership to that intended child account.
   Confirm the child can open, change and save the restored work and cannot
   access another child's work.
6. Keep the original backup until the restored copy has been verified.

Never repartition, format or reinstall the user's current disk as a recovery
shortcut without confirming the exact device and data-loss consequences.


# Build, hardware, and recovery notes

## Target hardware

The starting target is the user's specified **4 GB RAM and 32 GB storage** on an
x86-64 computer. For this project, treat it as the minimum design target, not a
verified compatibility statement. A larger display with at least 1024×768
resolution is preferred for readable controls; scaling and keyboard-only use
still need physical checks.

Recommended for more headroom: **8 GB RAM and 64 GB storage**. This is a project
planning recommendation, not a benchmark. The image release gate remains an
installed system/content footprint no greater than 20 GiB and at least 6 GiB
free on a 32 GB target after installation.

The current image uses Debian's `main` archive area only. Some Wi-Fi or graphics
devices may need firmware from Debian's `non-free-firmware` area. Check the
actual target hardware before relying on network setup; adding proprietary
firmware would need an explicit project policy and package review.

Firefox ESR is included for the KidsTube pilot. Debian lists the Trixie amd64
package at about 267 MB installed; measure the full image and remaining disk
space after installation rather than extrapolating from individual packages.

## Reproducible source build

Debian's official release page lists Debian 13 Trixie as current stable (13.7
at the 2026-10-30 design review):
[Debian releases](https://www.debian.org/releases/). Recheck this before each
image build.

Build from a supported Debian 13 amd64 host with `live-build`, network access to
the configured Debian archive, and sufficient free build space. From the
repository root:

```sh
sudo apt update
sudo apt install live-build
./scripts/prepare-chroot-assets
sudo lb config
sudo lb build
sha256sum live-image-amd64.hybrid.iso | tee live-image-amd64.hybrid.iso.sha256
```

The expected artifact is `live-image-amd64.hybrid.iso` in the repository root;
the adjacent `.sha256` file records its checksum. The first build downloads and
configures Debian packages and can take a while. Review and record the build
host release, package versions, image checksum, installed package list, image
size, installed footprint, and free disk space. Do not publish a test ISO as
ready for children until the account, session, accessibility, recovery, and
browser release gates have been checked.

## Test in a virtual machine

On the Debian build host, install QEMU and create a disposable 32 GB virtual
disk. The qcow2 file grows as data is written, so it does not immediately use
32 GB of host storage:

```sh
sudo apt install qemu-system-x86 qemu-utils
qemu-img create -f qcow2 eden-test.qcow2 32000000000
qemu-system-x86_64 \
  -m 4096 \
  -smp 2 \
  -cdrom live-image-amd64.hybrid.iso \
  -boot order=d \
  -drive file=eden-test.qcow2,format=qcow2,if=virtio
```

Boot the live environment first. For an installation test, start the Debian
installer from its menu and select only the disposable `eden-test.qcow2` disk.
This checks the 4 GB RAM / 32 GB storage configuration in a VM; it does not
replace testing the target computer's graphics, Wi-Fi, sound, touch, or UEFI.

## Test from a USB stick

For a first physical boot, copy the ISO file onto the data partition of your
Ventoy USB, reboot the test computer, open its one-time boot menu, and choose
the USB stick. Select the Eden ISO in Ventoy. Keep the ISO and checksum file
together so you can compare the checksum before booting. If you install Eden,
the installer erases the disk you select; use a spare test computer or drive
with anything important backed up. Do not select a disk containing files you
want to keep.

After the first boot, check adult sign-in and setup, create a test child account,
sign in through LightDM, open and close Tux Paint and KidsTube, check network-off
startup, and test the return-to-sign-in action. Record failures and hardware
details before changing the image.

## Recovery procedure for a test image

1. Keep an adult administrator account and its recovery password separate from
   the child account.
2. Back up child-created files to adult-managed removable storage before
   reinstalling. This prototype does not provide an automatic backup service.
3. If the child session fails, choose the normal desktop session from LightDM and
   use the adult account to inspect logs or restore the image. Do not diagnose
   system failures from the child account.
4. Reinstall from a verified ISO if package state is uncertain. Confirm the
   installer media checksum before use and re-create the adult and child
   accounts; do not restore unknown system files from a child's backup.
5. Test interrupted updates and rollback on a disposable device before offering
   unattended updates. No rollback mechanism is implemented yet.

## Verification still required

- Build ISO on Debian 13 amd64; `live-build` and QEMU are not available in the
  current work environment.
- Boot and install on representative 4 GB / 32 GB hardware, including UEFI and
  the actual display/input devices.
- Measure memory at idle and while Tux Paint runs; measure installed and free
  storage after updates.
- Test file saving, adult sign-in, child sign-in, session exit, keyboard and
  touch navigation, screen reader output, high contrast, text scaling, and
  recovery after interrupted installation/update.
- No hardware or ISO compatibility result is claimed yet.


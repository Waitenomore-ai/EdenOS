# EdenOS

An OS for children who struggle with school and learning.

# Eden OS

Eden OS is a Debian-based, child-friendly learning system in development.

## Current build target

- Debian 13 (Trixie), amd64
- 4 GB RAM and 32 GB storage starting target
- Lightweight XFCE base, GTK 4 Eden launcher, adult profile setup, child session, and shutdown flow source
- KidsTube is the only configured child browser destination; its Firefox allowlist still needs image-level testing
- The 20 GiB installed-system/content target and 6 GiB free-space target must be measured on real 32 GB hardware before release

## Build and test the installer image

Build on a Debian 13 amd64 host with network access and `live-build` installed.
The full commands, QEMU test, checksum step, and Ventoy USB instructions are in
[build and recovery notes](docs/build-and-recovery.md). The expected image is
`live-image-amd64.hybrid.iso` in the repository root. This repository is source
configuration only until a build has been completed and checked.

See [the adult first-run procedure](docs/first-run.md), [activity review](docs/activities.md), [browser safety gate](docs/browser-safety.md), and [build and recovery notes](docs/build-and-recovery.md) for current implementation limits and remaining checks.

## Safety and release status

This is an early development project, not a ready-to-install child operating system. Do not use it with a child until account separation, adult controls, accessibility, updates, recovery, and browser policy have been implemented and reviewed. KidsTube is a restricted browser pilot with an unverified allowlist, not a guarantee that every page or video is appropriate.

The current catalogue includes Tux Paint and four Eden-native offline prototypes: Number Meadow, Word Woodland, Story Garden, and Art Studio. Their source tests and package inclusion pass, but physical child-session usability is still unverified.

## Debian references

- [Debian 13 release information](https://www.debian.org/releases/trixie/)
- [Debian Live Manual](https://live-team.pages.debian.net/live-manual/html/live-manual/index.en.html)
- [live-build package in Trixie](https://packages.debian.org/trixie/live-build)
- [XFCE packages in Trixie](https://packages.debian.org/trixie/xfce4)
- [GTK 4 introspection package in Trixie](https://packages.debian.org/trixie/gir1.2-gtk-4.0)
- [Python GObject bindings in Trixie](https://packages.debian.org/trixie/python3-gi)
- [Firefox ESR in Trixie](https://packages.debian.org/trixie/web/firefox-esr)
- [AccountsService in Trixie](https://packages.debian.org/trixie/accountsservice)
- [MATE PolicyKit authentication agent in Trixie](https://packages.debian.org/trixie/mate-polkit)
- [Tux Paint in Trixie](https://packages.debian.org/trixie/tuxpaint)

## Build online

See [online build instructions](docs/online-build.md).


## Installed iMac updates

Use the development `eden-os-desktop` Debian artifact to update an existing EdenOS
installation without reinstalling the disk. See [installed update instructions](docs/updating-installed-eden.md).
The ISO remains installation/live-test media. Normal Radeon startup on the pilot
iMac is not yet reliable; its basic-graphics boot entry is the working fallback.

The [1,000-task backlog](docs/roadmap-1000.md) contains proposed OS work, app reviews
and custom-app projects. It is not a list of shipped features.

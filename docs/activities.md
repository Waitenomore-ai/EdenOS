# Eden OS activity review

This is the install and exposure register for child-facing activities. An activity
must be reviewed here and marked `reviewed: true` in the local catalogue before
the child shell displays it. A catalogue entry alone does not install software.

| Activity | Category | Debian package / desktop ID | Offline | Licence and age notes | Accessibility and maintenance review |
| --- | --- | --- | --- | --- | --- |
| Tux Paint | Create | `tuxpaint` / `tuxpaint.desktop` | Yes, after installation | Free and open source, GPL-2.0; designed for children approximately 3–12 | No account, ads, or network needed for core drawing. Verify keyboard, touch, screen-reader, and sensory settings on target hardware before calling it accessible. Recheck package availability and upstream licence on each Debian release update. |

Sources checked 2026-10-30: [Debian Trixie package record](https://packages.debian.org/trixie/tuxpaint), [Tux Paint licence](https://tuxpaint.org/download/), and [Tux Paint age range](https://tuxpaint.org/).

## Current limits

- This is a package and upstream-documentation review, not a child usability or
  accessibility certification.
- Debian package installation, icon display, app launch, and offline operation
  still need to be checked in a built image.
- GCompris is a candidate for a later review. Do not install or expose it until
  the automatic external-asset download behavior has a verified offline-safe
  default and the adult-facing choice is clear.
- Adult administrators should be able to remove an activity from the home screen
  independently from uninstalling its package.

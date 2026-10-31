# Eden OS activity review

This is the install and exposure register for child-facing activities. An activity
must be reviewed here and marked `reviewed: true` in the local catalogue before
the child shell displays it. A catalogue entry alone does not install software.

| Activity | Category | Debian package / desktop ID | Offline | Licence and age notes | Accessibility and maintenance review |
| --- | --- | --- | --- | --- | --- |
| Tux Paint | Create | `tuxpaint` / `tuxpaint.desktop` | Yes, after installation | Free and open source, GPL-2.0; designed for children approximately 3–12 | No account, ads, or network needed for core drawing. Verify keyboard, touch, screen-reader, and sensory settings on target hardware before calling it accessible. Recheck package availability and upstream licence on each Debian release update. |
| Number Meadow | Learn | Eden native / `eden-number-meadow.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Four-answer counting rounds with large controls. Display and child usability still need physical-image testing. |
| Word Woodland | Learn | Eden native / `eden-word-woodland.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | First-letter matching with familiar words and large controls. Phonics suitability and physical usability still need review. |
| Story Garden | Read | Eden native / `eden-story-garden.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Four-scene picture story with restart control. Reading level and physical usability still need review. |
| Art Studio | Create | Eden native / `eden-art-studio.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Sticker-board activity with undo and clear. It is not a replacement for full drawing software. |
| Puzzle Pond | Play | Eden native / `eden-puzzle-pond.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Four-pair matching game with no timer or score. Physical usability still needs review. |
| Time and Routines | Play | Eden native / `eden-time-routines.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Four-step visual checklist with restart. It is a support tool, not a clinical schedule. |
| Nature Explorer | Play | Eden native / `eden-nature-explorer.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Six-card observation activity with large controls and no timer or score. Outdoor safety and physical usability still need review. |
| Feelings and Quiet Space | Play | Eden native / `eden-feelings.desktop` | Yes | Eden-native prototype; no network, account, or saved progress | Non-diagnostic feeling words and gentle actions. It must not be presented as medical or mental-health treatment. |

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


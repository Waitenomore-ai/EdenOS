# Eden OS native iMac visual acceptance gaps — 18 November 2026

Reference: read-only live iMac screenshot at
`/mnt/dripvid-backup-2tb/Eden_Development/imac-visual-baseline-20261118/imac-live-1920x1080.png`.
Target: Windows/macOS PySide6 native app. Live iMac and website must not be modified.

## Confirmed from direct 1920x1080 screenshot comparison

- **Play category:** The iMac shows six large illustrated entries in two rows:
  Story Garden, Puzzle Pond, Meadow Match, Nature Explorer, Feelings & Calm, Find Me.
  The native app currently has four implemented entries; Meadow Match and Find Me are
  not yet ported. Their *exact* preferred PNG button art is recovered in
  `assets/imac-activity-cards/`, but they must not be shown as working until their
  games are implemented.
- **Character:** The iMac Play category overlays the child's full-body figure in
  the lower-left foreground. Native category view does not yet include this.
- **Wallpaper:** Native category screen now uses a curated garden wallpaper but
  does not yet guarantee the identical per-child wallpaper selected on the iMac.
- **Layout:** iMac uses a 4-column first row with two more tiles on the second
  row, 360px activity tiles and image-led controls. Native tiles are image-led
  and have accessibility names, but pixel-alignment remains to be measured.
- **Story Garden:** Approved banner and wood selection graphics recovered;
  native reader still lacks the original iMac page composition and companion
  layering. 148 original page-art files recovered; 762 audio MP3s exist in the
  project, but human voice and physical audio playback require verification.
- **Art Studio:** Native sidebar increased to 260px with two-column colours to
  prevent clipping seen in Windows screenshot. Direct Windows acceptance still needed.
- **Other screens:** Learn, Profiles, Rewards and wallpaper selection require
  direct side-by-side iMac comparisons.

## Do not claim completion until

1. Meadow Match and Find Me behaviours are implemented and safe per child.
2. Every marked screen is compared at 1920x1080 and at 1366x768.
3. Story art and narration mappings are tested against the available iMac source,
   with missing pages and voice files reported (never invented).
4. Art Studio's sidebar and toolbar are fully visible on Windows.
5. Windows/macOS builds pass automated and physical-device accessibility tests.
6. Chris approves the final visual parity. No live deployment before approval.

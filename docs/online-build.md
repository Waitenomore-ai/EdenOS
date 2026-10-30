# Build Eden OS online

The GitHub Actions workflow builds a development ISO on a temporary Ubuntu
runner using a privileged Debian 13 container. It runs manually, needs no API
keys, has read-only repository permission, and does not publish a release.
A remote test ISO built successfully on 30 October 2026 (run 41072943583). That image predates the Garden of Eden branding. The rebuilt branded image has not yet been verified.

1. Create a GitHub repository named `eden-os`. Private keeps development source
   private; build minutes and artifact storage are subject to your account's
   allowances. Check billing before running if you have enabled paid usage.
2. Extract the source ZIP. Upload the CONTENTS of the `eden-os` folder at the
   repository root, including `.github/workflows/build-iso.yml`. Uploading the
   ZIP alone will not install the workflow. If your file picker hides `.github`,
   create `.github/workflows/build-iso.yml` using GitHub's Add file editor and
   paste in the supplied workflow.
3. Commit to the default branch. Open Actions, select Build Eden OS ISO, and
   choose Run workflow on the default branch.
4. After success, download the `eden-os-test-iso-N` artifact and extract it.
   This contains the ISO, checksum, and build information. Artifacts expire
   after seven days; download them promptly. Failed builds retain their log
   if the build reached the logging step.
5. On Windows, use `Get-FileHash .\eden-os-amd64-test.iso -Algorithm SHA256`
   and compare the result with the checksum file.
6. Boot-test the ISO on a disposable VM or a spare computer using Ventoy.
   Building online does not verify child controls, browser filtering,
   accessibility, installation, recovery, or hardware compatibility.

The workflow uses GitHub's checkout and artifact actions v6 and Debian's
`trixie` container tag. These version tags and package archives can change;
this is an automated source build, not a byte-for-byte reproducible build.

## Branding gate

The manual workflow has `require_branding` enabled by default. To build a branded ISO, first place `edenos-artwork/logo/edenos-logo.png` and all six named Garden of Eden PNGs in `edenos-artwork/wallpapers/` in the repository. The build validates artwork and stages default LightDM and XFCE wallpapers. Leave `require_branding` enabled to avoid distributing an image without its artwork. A successful workflow still requires real BIOS/UEFI boot tests and checks of the actual desktop and child accounts.


## Interpreting the optional boot diagnostic

The BIOS smoke helper fails if QEMU cannot start or exits unexpectedly, and
keeps its output in `output/qemu-bios-smoke.log`. A normal 100-second timeout
is explicitly **inconclusive**: it is not proof that the guest reached a login
screen. A normal emulator exit without a detected error is also not a verified
boot. Explicit kernel panic, missing-root, and boot-device errors fail the check.
This helper tests BIOS only; Intel iMac UEFI boot still needs a separate check.

## Roadmap build update — 30 October 2026

The approved logo and all six wallpapers are now committed under edenos-artwork.
Builds embed /etc/eden-os/build.json (version, UTC build time and source commit).
The build first runs a real GTK construction/navigation smoke test under Xvfb.
The optional boot_smoke input now runs both BIOS and UEFI/OVMF diagnostics with
4 GB guest RAM; timeouts remain inconclusive. See roadmap-100.md for per-item
status and release-evidence.md for outstanding device tests.

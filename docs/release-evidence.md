# Evidence required for an EdenOS test release

Record source commit, build date, ISO SHA-256, firmware mode, machine model,
RAM, physical disk capacity, install target and test results. Distinguish a
file/configuration check from a real boot, successful installation and usable
child session. Source version is embedded in /etc/eden-os/build.json.

Boot diagnostics are attempted firmware boots only. Timeout is inconclusive.
UEFI uses OVMF with copied disposable variables; neither BIOS nor generic OVMF
results guarantee Intel iMac compatibility, especially models with 32-bit EFI.

Use a disposable virtual disk of exactly 32000000000 bytes for the 32 GB test:
`qemu-img create -f qcow2 eden-test.qcow2 32000000000`. A `32G` virtual disk is
32 GiB and exceeds the stated device target. Never substitute a host block
device in the guest's drive arguments.

Release checklist:
- BIOS and UEFI visually reach live login and the Eden launcher.
- Disposable install boots without installer media; adult sign-in works.
- Child standard account cannot perform admin actions or reach unintended
  desktops/settings/tools through ordinary shortcuts, dialogs, or app exits.
- Activity launches offline, saves/reopens work, closes back to Eden, and each
  child's work remains private from other standard accounts.
- Keyboard focus, high contrast, maximum text scale, screen reader and supported
  touch operation are tested and results limited to behaviours observed.
- Shutdown, sign-out, save failures, low space and interrupted updates tested.
- RAM and installed/free storage measured on representative hardware.
- Browser remains disabled unless service suitability, policy enforcement,
  bypass tests, adult configuration and data clearing have been checked.

A full-screen launcher is not a security boundary. The current child-session
script starts xfwm4 and Eden, but comprehensive session restrictions, alternate
login sessions and direct Firefox launches are not verified. Keep supervised
development use separate from release approval.

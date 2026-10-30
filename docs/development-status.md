# Eden OS continuation — 30 October 2026

Resumed from eden-os-test-source.zip (archive source commit 067cd23a).

## Verified in this continuation

- Original 14 Python unit tests passed.
- Reproduced a child-setup bug: control characters were accepted in passwords,
  although OpenSSL's line-oriented input can truncate the password.
- Added rejection in both form validation and hashing. Ordinary spaces and
  printable Unicode remain accepted.
- Three new regression tests failed before the fix (10 failing subcases), then
  all 17 tests passed after the fix. Tests use the real OpenSSL executable.
- Changes reviewed locally; no remote repository or deployment changed.

## Next build gate

This workspace runs Ubuntu 24.04 and has neither live-build nor QEMU. No ISO
was produced or boot-tested. Use the documented Debian 13 builder procedure.
The VM disk example uses 32G (32 GiB), which is larger than a marketed 32 GB
physical drive; use 32000000000 bytes for a representative capacity test.

The archive's browser defaults enable an explicitly unverified KidsTube pilot.
This differs from the earlier design's disabled-until-verified gate. Preserved
here pending recovery of the later decision; do not treat the pilot as release
verified. Its bypass, policy, and playback checks remain open.

Remaining checks: GUI on Debian, account creation/cleanup through PolicyKit,
adult handoff, child escape routes, offline app saving, browser enforcement,
installation, recovery, memory usage, and physical 32 GB storage measurements.

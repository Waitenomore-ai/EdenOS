# EdenOS reliability fixes — 30 October 2026

Based on main at 9ecbfade8fc2ea05918e850a0c331895012029d8.

- Boot diagnostics now reject QEMU startup/crash/tool failures instead of
  silently returning success. Timeout output explicitly says inconclusive.
- Accessibility changes are persisted before updating the in-memory settings.
  Filesystem errors keep the old settings and show a message asking an adult
  for help rather than leaking an exception out of the GTK callback.
- Added six diagnostic tests and two preference callback tests. All 25 tests
  passed locally. Each fix was reproduced before implementation.

The preference tests use real file writes and a controlled failing filesystem
path. GTK imports are stubbed because this environment has no GTK runtime;
visual validation is still needed on Debian. The boot tests execute the real
helper and GNU timeout with a controlled QEMU executable; no ISO boot was tested.

No disk, partition, installer, firmware, or existing ISO was changed. These
fixes must be included in a future ISO build to reach installed devices.

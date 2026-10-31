# Installed updates and hardware foundation

User authority: implement the 1,000-task backlog, deploy tested work and produce an
ISO; provide an update route for the installed iMac. The full backlog is an
ongoing multi-project programme. This first executable milestone addresses the
confirmed missing-firmware image gap and absence of an installed update artifact.

## Tasks

1. Build a Debian update artifact. Verify real extraction, dependencies, wrapper
   permissions, rejection of invalid versions, preservation boundaries and lack
   of bytecode caches. Do not run package installation on the DripVid server.
2. Include Radeon firmware and diagnostics in future images; add adult launcher
   discoverability. Do not claim accelerated iMac graphics is fixed.
3. Automate a fast update build and a full ISO build from the same source.
4. Document physical iMac update acceptance and recovery. Publish the expanded
   backlog with stable IDs and record hardware-only items as pending.
5. Run the full source suite, obtain a fresh review, publish source changes,
   dispatch both workflows and report their actual artifact status.

Ruling: use standard adult-installed apt packages, not a privileged git-pull or
remote-script updater. Package creation tests do not certify real installation.
No disk formatting, server service changes, automatic reboot or iMac GRUB changes
are part of this milestone.

# Eden OS Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first Eden OS source project: a reproducible Debian live-build configuration and a child-ready experience prototype, ready for a Debian build host.

**Architecture:** Use a live-build configuration for Debian 13 x86-64 with a lightweight XFCE base and a separate Eden child session. Add adult profile setup and a child launcher, keeping administration protected and child accounts standard users. KidsTube has a restricted development pilot; its allowlist and playback still require image-level checks.

**Tech Stack:** Debian live-build, XFCE, Python 3 with GTK 4, Debian package configuration.

**Spec:** `docs/superpowers/specs/2026-10-30-eden-os-design.md`

## Global Constraints

- Target hardware is 4 GB RAM and 32 GB storage.
- Debian 13 “Trixie” stable is the design-time base; verify current stable and packages before image build.
- The first architecture is x86-64.
- Default installed OS and content target is no more than 20 GiB; preserve at least 6 GiB free on the target drive.
- Child daily use must not require administrator privileges or an internet connection for included offline activities.
- Do not claim browser safety, specialist accessibility, or compatibility until checked.
- Do not add telemetry or child cloud accounts.

## Review Focus

- 32 GB devices expose less usable capacity than the printed number: image build must report installed and free space.
- Child users must not access adult settings or a terminal through ordinary navigation.
- Keyboard focus and text scaling must remain usable across launcher screens.
- Missing network must not break the child home screen or offline apps.
- A missing, malformed, or broadened KidsTube policy must leave the child shortcut unavailable; general browsing remains blocked.

---

### Task 1: Establish the Eden OS source layout and live-build configuration

**Files:**
- Create: `auto/config`
- Create: `config/package-lists/eden.list.chroot_install`
- Create: `config/includes.chroot/etc/eden-os/defaults.json`
- Create: `README.md`
- Create: `.gitignore`

**Interfaces:**
- Produces: a documented x86-64 live-build configuration targeting Debian 13 stable; package list is the single source for image package selection.

- [x] Create the directory structure and README with supported target, build prerequisites, and a clear description of KidsTube's unverified restricted pilot.
- [x] Define the Debian stable suite and minimal XFCE/GTK runtime packages in the repeatable `auto/config` and package list; avoid optional applications until their licence and offline behaviour are reviewed.
- [x] Set conservative first-run defaults: KidsTube-only restricted pilot, progress disabled, and no child account created before adult setup.
- [x] Record the installed-size and remaining-space check required for any image release.
- [x] Review generated configuration for secrets, stale release names, and ensure no general browser access is enabled.

Ruling for Task 1: Defer child account creation to Task 3’s adult first-run setup so the image contains no shared/default child password and no account is created before an adult chooses profile details.

### Task 2: Build the Eden child home-screen prototype

**Files:**
- Create: `eden-shell/eden_shell/` focused modules for window, navigation, activity catalogue, and preferences
- Create: `eden-shell/data/` for original icons and themes
- Create: `eden-shell/pyproject.toml`
- Create: `eden-shell/README.md`

**Interfaces:**
- Consumes: local activity catalogue and local accessibility preferences.
- Produces: a full-screen launcher with Learn, Play, Read, Create, My Progress, Home, and Adult Help entry points.

- [x] Define accessible labels, predictable navigation order, scalable type, high-contrast theme option, and reduced-motion preference.
- [x] Build the launcher navigation without requiring accounts or network access.
- [x] Show only activities present in the local reviewed catalogue; show a calm empty state when a category has no activity.
- [x] Keep progress off by default and store any enabled progress locally only.
- [ ] Review keyboard-only operation, window sizing, text scaling, and offline startup on a Debian 13 development system.

### Task 3: Integrate setup, child session, and adult handoff

**Files:**
- Create: `/etc/skel/` child account desktop shortcut
- Create: `config/includes.chroot/usr/share/xsessions/eden-child.desktop`
- Create: a first-run setup application for adult account and child profile creation
- Create: a session startup script and authenticated adult return-to-login action
- Create: startup and shutdown experience configuration

**Interfaces:**
- Consumes: the launcher executable from Task 2.
- Produces: guided adult setup, a separate Eden child session, protected adult handoff, and calm startup/shutdown states.

- [x] Configure child login to launch the Eden shell instead of a full desktop panel.
- [x] Configure a clearly visible return-to-sign-in action; adult sign-in remains behind LightDM authentication.
- [x] Create child accounts as AccountsService standard users and keep adult settings outside the child session.
- [x] Document that child session restrictions are usability controls, not a substitute for physical supervision.
- [ ] Review ordinary keyboard shortcuts and app-exit paths for accidental access to desktop settings or a terminal.
- [ ] Check the shutdown confirmation and power-off request in the image; confirm it does not delay shutdown or hide save failures from an adult.

### Task 4: Add a reviewed offline activity pack

**Files:**
- Create: `config/package-lists/eden-activities.list.chroot_install`
- Create: `docs/activities.md`

**Interfaces:**
- Consumes: Task 1 image package list and Task 2 local activity catalogue.
- Produces: a compact default set of offline activities for literacy, numeracy, creativity, and problem-solving.

- [x] Check Debian package availability, licence, age suitability, accessibility, offline behaviour, and maintenance for each proposed app.
- [x] Add only approved candidates; otherwise leave the category available but empty.
- [ ] Confirm app launch and return-to-home behaviour in the child session.
- [ ] Measure package and installed disk usage against the 20 GiB OS/content budget.

### Task 5: Prepare the browser pilot gate

**Files:**
- Create: `docs/browser-safety.md`
- Create: Firefox policy and KidsTube shortcuts; adult setup browser preference UI remains future work.

**Interfaces:**
- Consumes: adult preferences from Task 2 and child session from Task 3.
- Produces: general browsing disabled; KidsTube-only pilot uses a fail-closed allowlist and documented limitations.

- [x] Identify the exact KidsTube website and check its current suitability and privacy disclosures.
- [x] Select Firefox ESR's system WebsiteFilter allowlist for a restricted pilot; confirm embedding requirements on the actual site.
- [ ] Verify the policy and embedded playback on the target browser; document known bypasses and limits.
- [x] Make the launcher fail closed when the required allowlist is absent or invalid. Image-level policy verification remains open.

### Task 6: Build and assess a test image

**Files:**
- Create: `docs/build-and-recovery.md`
- Create: build scripts and image validation output.

**Interfaces:**
- Consumes: live-build configuration, launcher, session integration, and reviewed activity set.
- Produces: an installable test image and a documented result for the 4 GB / 32 GB target.

- [ ] Build on a supported Debian 13 x86-64 host with live-build.
- [ ] Install and boot on representative 4 GB / 32 GB hardware.
- [ ] Confirm cold boot, adult setup, authenticated handoff, offline activity launch, saving, shutdown, and recovery after interrupted update.
- [ ] Measure memory, installed space, and free space under normal child use.
- [ ] Publish only as a test image until browser and accessibility release gates are met.

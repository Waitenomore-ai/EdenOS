# Eden OS First Build Design

## Intent

Create an installable, child-friendly Debian system that feels welcoming and predictable, works offline for everyday learning, and gives adults a separate place to configure it. The first build proves the core experience on the user’s starting hardware target before expanding the app library or making strong claims about browser filtering.

## Goals

- Provide a simple first-time setup for an adult and a clear home screen for a child.
- Offer a small set of reviewed, offline learning and creative activities.
- Make common accessibility options easy to find and adjust.
- Keep adult administration separate from the child’s everyday account.
- Minimise child data collection; keep progress on-device and optional.
- Run acceptably on a computer with 4 GB RAM and 32 GB storage.

## Non-goals for the first build

- Guarantee every website or video is appropriate.
- Cloud accounts, online progress syncing, public rankings, or telemetry.
- A large preinstalled catalogue of games.
- Every processor architecture or specialist input device.
- Claims that switch access or other specialist accessibility works before testing.

## Approaches

1. **Custom Debian installer image (selected):** use Debian live-build to create an installable image with Eden configuration integrated. This gives the product a joined-up setup and startup experience, with additional image maintenance.
2. **Eden setup layered onto standard Debian:** quicker to prototype, but less control over the complete experience.

The user selected the custom installer image.

## Proposed architecture

- Debian 13 “Trixie” stable, using official Debian live-build tools. Recheck the current release and package choices immediately before implementation.
- x86-64 first; consider other architectures later.
- Lightweight XFCE base, configured to stay out of the child’s way.
- Full-screen Eden launcher with Learn, Play, Read, Create, and My Progress. First implementation proposal: a small GTK application, subject to accessibility checks.
- A child account without administrator rights, and a protected adult administrator account. Adult settings and app installation stay out of the child’s normal session.
- Browser support is included in the design but unavailable until an adult configures it. Use a curated-sites model only after verifying enforcement and testing escape routes. KidTube is optional pending identification and suitability review.
- Target no more than 20 GiB for the installed OS and default content, leaving at least 6 GiB free on a 32 GB device for updates and saved work. Validate actual usage on target hardware.
- No telemetry by default. Optional progress stays on-device. Explain network access during adult setup.

## First-build experience

1. Power-on shows a short, calm welcome and clear loading state without technical error messages in the child-facing flow.
2. Adult setup creates or chooses a child profile, selects text and sound preferences, chooses activities, and decides whether to enable the browser.
3. Child opens activities from a consistent home screen and returns home through a visible control. Keyboard navigation is baseline; touch is tested when supported.
4. Adult enters the protected area to change profiles, activities, accessibility preferences, and browser choices.
5. Shutdown clearly offers to save and power off without pressure or unnecessary delay.

## Initial activities

Start with a small selection for literacy, numeracy, creativity, and problem-solving. GCompris and Tux Paint are candidates, not confirmed inclusions. Check each candidate’s current Debian package, licence, age suitability, offline use, accessibility, and maintenance before adding it.

## Release gates

- Browser enforcement must be implemented and its limitations documented before enabling browser use for children.
- Child-session escape routes must be checked; a full-screen launcher alone is not a security boundary.
- The 32 GB storage target must be confirmed on real hardware.
- Accessibility claims must be limited to behaviours actually checked.
- Recovery, updates, saving, shutdown, and offline learning must be checked before calling the image a usable test release.

## Constraints and assumptions

- Target: 4 GB RAM / 32 GB storage, supplied by the user.
- Initial architecture: x86-64, proposed for the first prototype.
- Debian base: Debian 13 stable, verified as current at design time.
- No exact KidTube service URL or safety suitability has been confirmed.
- The current build environment lacks live-build and QEMU, so a bootable ISO cannot be honestly claimed from this environment without a suitable builder.

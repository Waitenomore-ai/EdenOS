Warning: truncated output (original token count: 19818)
Total output lines: 1259

# EdenOS — 1,000-task development and app backlog

Prepared 30 October 2026. Proposed checklist, not a claim that 1,000 features are missing or approved for installation.

## Starting point

EdenOS is based on Debian 13. The Kingston installation passed filesystem and boot-file checks. The iMac reaches the graphical login and adult desktop in basic-graphics mode; normal Radeon startup has produced a black screen. The launcher and child-session experience still need physical-device verification. Existing source features should be checked before implementing replacements.

This document expands the earlier 100-item roadmap. Its IDs E0001–E1000 are a new planning index; they do not replace or imply completion of the original roadmap IDs. All boxes start unchecked because this is a proposed backlog, not a fresh audit of the repository or hardware.

## How to use this list

- **First priority:** sections 1–5, with boot stability and the first usable child session ahead of extra applications.
- **Foundation:** sections 6–30. Prioritise security, accessibility, storage and recovery according to release blockers.
- **Review candidates:** sections 31–40. Research and test before approving an app; reject unsuitable or duplicate candidates rather than installing everything.
- **Build proposals:** sections 41–50. Each app is a separate project requiring a small prototype and a scoped decision before a full implementation.
- For each selected task, record an owner, dependencies, acceptance evidence and status. Mark existing work verified instead of rebuilding it.
- Do not treat every item as a requirement for the first release. Select a small milestone and keep the default image lean.
- Third-party apps still need current package availability, licence, age suitability, accessibility, network behaviour and installed-size checks. Mention here is not approval.
- No cloud AI service, subscription, online child account or production deployment is authorised merely by inclusion in this list.

## Index

| IDs | Section | Work type |
| --- | --- | --- |
| E0001–E0020 | Boot and immediate iMac fixes | OS / validation |
| E0021–E0040 | Launcher and first child session | OS / validation |
| E0041–E0060 | Installer and drive selection | OS / validation |
| E0061–E0080 | ISO and release images | OS / validation |
| E0081–E0100 | Bootloader and kernel maintenance | OS / validation |
| E0101–E0120 | Hardware coverage | OS / validation |
| E0121–E0140 | Power and session reliability | OS / validation |
| E0141–E0160 | Accounts and authentication | OS / validation |
| E0161–E0180 | Adult setup and controls | OS / validation |
| E0181–E0200 | Child session boundaries | OS / validation |
| E0201–E0220 | App launching and catalogue | OS / validation |
| E0221–E0240 | Home screen and navigation | OS / validation |
| E0241–E0260 | Visual identity and branding | OS / validation |
| E0261–E0280 | Accessibility foundations | OS / validation |
| E0281–E0300 | Language and reading accessibility | OS / validation |
| E0301–E0320 | Local data and privacy | OS / validation |
| E0321–E0340 | Browser and web access | OS / validation |
| E0341–E0360 | Connectivity and peripherals | OS / validation |
| E0361–E0380 | Performance and storage | OS / validation |
| E0381–E0400 | Updates and package management | OS / validation |
| E0401–E0420 | Backup and restoration | OS / validation |
| E0421–E0440 | Diagnostics and support | OS / validation |
| E0441–E0460 | Automated verification | OS / validation |
| E0461–E0480 | Manual quality assurance | OS / validation |
| E0481–E0500 | Packaging and build engineering | OS / validation |
| E0501–E0520 | Release management | OS / validation |
| E0521–E0540 | Documentation and onboarding | OS / validation |
| E0541–E0560 | Content governance and licensing | OS / validation |
| E0561–E0580 | App distribution and optional packs | OS / validation |
| E0581–E0600 | Pilot feedback and project tracking | OS / validation |
| E0601–E0620 | Existing app candidates: early learning | Review / integration |
| E0621–E0640 | Existing app candidates: literacy | Review / integration |
| E0641–E0660 | Existing app candidates: numeracy | Review / integration |
| E0661–E0680 | Existing app candidates: typing and coding | Review / integration |
| E0681–E0700 | Existing app candidates: drawing and making | Review / integration |
| E0701–E0720 | Existing app candidates: music and media | Review / integration |
| E0721–E0740 | Existing app candidates: geography and science | Review / integration |
| E0741–E0760 | Existing app candidates: puzzles and board games | Review / integration |
| E0761–E0780 | Existing app candidates: accessible utilities | Review / integration |
| E0781–E0800 | Existing app candidates: adult and classroom tools | Review / integration |
| E0801–E0820 | Build Eden Story Garden | Build proposal |
| E0821–E0840 | Build Eden Number Meadow | Build proposal |
| E0841–E0860 | Build Eden Word Woodland | Build proposal |
| E0861–E0880 | Build Eden Art Studio | Build proposal |
| E0881–E0900 | Build Eden Music Grove | Build proposal |
| E0901–E0920 | Build Eden Puzzle Pond | Build proposal |
| E0921–E0940 | Build Eden Nature Explorer | Build proposal |
| E0941–E0960 | Build Eden Time and Routines | Build proposal |
| E0961–E0980 | Build Eden Feelings and Quiet Space | Build proposal |
| E0981–E1000 | Build Eden Maker Lab and personal workspace | Build proposal |

## 1. Boot and immediate iMac fixes

- [ ] **E0001** — Record the exact iMac model identifier.
- [ ] **E0002** — Record the Radeon PCI device ID.
- [ ] **E0003** — Capture a successful basic-graphics boot log.
- [ ] **E0004** — Capture the failed accelerated-graphics boot log.
- [ ] **E0005** — Check whether the black screen also affects an external monitor.
- [ ] **E0006** — Confirm installed Radeon firmware matches the detected GPU.
- [ ] **E0007** — Confirm firmware is included in every installed initramfs.
- [ ] **E0008** — Check the Radeon driver for model-specific boot errors.
- [ ] **E0009** — Test one documented Radeon workaround at a time.
- [ ] **E0010** — Add a reversible basic-graphics default for this iMac.
- [ ] **E0011** — Preserve a normal-graphics entry for controlled testing.
- [ ] **E0012** — Verify the basic-graphics setting survives kernel updates.
- [ ] **E0013** — Confirm graphical login after three cold boots.
- [ ] **E0014** — Confirm graphical login after three warm restarts.
- [ ] **E0015** — Measure the delay between power-on and login.
- [ ] **E0016** — Verify display resolution in basic-graphics mode.
- [ ] **E0017** — Verify pointer movement and keyboard input at login.
- [ ] **E0018** — Verify the monitor wakes after display blanking.
- [ ] **E0019** — Document a recovery route if graphical login fails.
- [ ] **E0020** — Record the first reproducible iMac boot configuration.

## 2. Launcher and first child session

- [ ] **E0021** — Confirm eden-shell launches from the adult terminal.
- [ ] **E0022** — Capture launcher errors when using software rendering.
- [ ] **E0023** — Test a supported GTK renderer when GPU acceleration is unavailable.
- [ ] **E0024** — Verify the launcher fills the iMac screen.
- [ ] **E0025** — Confirm the child session entry appears at login.
- [ ] **E0026** — Create a test child account through Eden setup.
- [ ] **E0027** — Verify the child account launches Eden automatically after login.
- [ ] **E0028** — Verify the adult account still opens its administration desktop.
- [ ] **E0029** — Confirm the child session starts its window manager.
- [ ] **E0030** — Test returning to Eden after closing Tux Paint.
- [ ] **E0031** — Verify all five home categories are reachable.
- [ ] **E0032** — Display a useful message when a category has no apps.
- [ ] **E0033** — Test launcher navigation after a failed app launch.
- [ ] **E0034** — Verify child preferences survive logout.
- [ ] **E0035** — Confirm child preferences are separate from adult preferences.
- [ ] **E0036** — Verify logout returns to the graphical login screen.
- [ ] **E0037** — Test shutdown from inside the child session.
- [ ] **E0038** — Document how an adult returns to administration.
- [ ] **E0039** — Remove confusing first-run instructions that imply Debian is an error.
- [ ] **E0040** — Record screenshots of the actual installed child experience.

## 3. Installer and drive selection

- [ ] **E0041** — Show EdenOS branding on the installer landing screen.
- [ ] **E0042** — Explain live testing versus permanent installation.
- [ ] **E0043** — Display disk model and capacity before selection.
- [ ] **E0044** — Distinguish the installer USB from the internal disk.
- [ ] **E0045** — Require explicit selection before offering whole-disk erase.
- [ ] **E0046** — Show the target disk serial suffix in the erase summary.
- [ ] **E0047** — Explain that replacing an OS removes existing files.
- [ ] **E0048** — Keep partition preview visible before committing changes.
- [ ] **E0049** — Prevent automatically selecting the server operating-system disk.
- [ ] **E0050** — Validate available target space before installation.
- [ ] **E0051** — Offer an accessible keyboard-driven installation route.
- [ ] **E0052** — Provide a guided EFI partition layout.
- [ ] **E0053** — Define when an existing EFI partition can be reused.
- [ ] **E0054** — Check that installed fstab entries use filesystem UUIDs.
- [ ] **E0055** — Remove live-media apt sources from the installed system.
- [ ] **E0056** — Test DNS access using the package-manager service account.
- [ ] **E0057** — Prevent services from starting inside installation chroots.
- [ ] **E0058** — Isolate installer mounts in a private mount namespace.
- [ ] **E0059** — Detect incomplete installations and offer a defined recovery path.
- [ ] **E0060** — Verify all target partitions are safely unmounted at completion.

## 4. ISO and release images

- [ ] **E0061** — Include the firmware repository needed by supported hardware.
- [ ] **E0062** — Define the minimum supported firmware package set.
- [ ] **E0063** — Include pciutils for hardware diagnostics.
- [ ] **E0064** — Include a clear offline troubleshooting guide on the ISO.
- [ ] **E0065** — Give the ISO an identifiable build number.
- [ ] **E0066** — Show source revision in the installed About screen.
- [ ] **E0067** — Publish an image checksum beside each download.
- [ ] **E0068** — Validate downloaded image checksums before USB creation.
- [ ] **E0069** — Verify the ISO contains the expected root filesystem.
- [ ] **E0070** — Check that both BIOS and EFI boot entries exist.
- [ ] **E0071** — Verify the amd64 EFI fallback executable.
- [ ] **E0072** — Decide whether 32-bit EFI support belongs in a separate image.
- [ ] **E0073** — Test the ISO with Rufus raw-image writing.
- [ ] **E0074** — Test the ISO with a second USB-writing tool.
- [ ] **E0075** — Test a USB written from Linux.
- [ ] **E0076** — Test a USB written from macOS.
- [ ] **E0077** — Document supported USB boot modes by machine.
- [ ] **E0078** — Reject release uploads missing required artwork.
- [ ] **E0079** — Keep a known-working image available for rollback.
- [ ] **E0080** — Record which image was used for each hardware test.

## 5. Bootloader and kernel maintenance

- [ ] **E0081** — Make the GRUB menu readable at low resolution.
- [ ] **E0082** — Keep normal and recovery boot entries clearly named.
- [ ] **E0083** — Provide a one-time basic-graphics option.
- [ ] **E0084** — Provide a text-only recovery boot option.
- [ ] **E0085** — Ensure the boot menu never targets a different attached OS by accident.
- [ ] **E0086** — Preserve at least one known-working kernel.
- [ ] **E0087** — Test initramfs regeneration after firmware installation.
- [ ] **E0088** — Test boot after installing a newer kernel.
- [ ] **E0089** — Test boot after removing an obsolete kernel.
- [ ] **E0090** — Verify EFI files reside on the selected target disk.
- [ ] **E0091** — Verify bootloader installation does not change another machine's NVRAM.
- [ ] **E0092** — Test EFI fallback boot without a saved firmware entry.
- [ ] **E0093** — Test BIOS boot on a machine that requires it.
- [ ] **E0094** — Check root UUID references after filesystem restoration.
- [ ] **E0095** — Validate GRUB configuration syntax during release checks.
- [ ] **E0096** — Generate recovery entries through maintainable configuration.
- [ ] **E0097** — Prevent future update-grub runs losing required custom entries.
- [ ] **E0098** — Test boot with the installer USB removed.
- [ ] **E0099** — Test boot with an unrelated USB storage device attached.
- [ ] **E0100** — Document manual boot selection without erasing any disk.

## 6. Hardware coverage

- [ ] **E0101** — Create a supported-machine inventory.
- [ ] **E0102** — Record CPU architecture for each test machine.
- [ ] **E0103** — Record installed RAM for each test machine.
- [ ] **E0104** — Record GPU and display connector for each test machine.
- [ ] **E0105** — Test built-in Ethernet discovery.
- [ ] **E0106** — Test wired network reconnection after sleep.
- [ ] **E0107** — Test supported Wi-Fi adapters without Ethernet.
- [ ] **E0108** — Test Wi-Fi reconnect after restart.
- [ ] **E0109** — Test Bluetooth keyboard pairing with adult approval.
- [ ] **E0110** — Test built-in speakers.
- [ ] **E0111** — Test headphone insertion and removal.
- [ ] **E0112** — Test microphone access only in an approved activity.
- [ ] **E0113** — Test volume buttons.
- [ ] **E0114** — Test brightness controls.
- [ ] **E0115** — Test webcam discovery without enabling recording.
- [ ] **E0116** — Test USB mouse hot-plugging.
- [ ] **E0117** — Test a UK keyboard layout.
- [ ] **E0118** — Test a compact keyboard missing dedicated function keys.
- [ ] **E0119** — Test battery status on a supported laptop.
- [ ] **E0120** — Test thermal and fan behaviour during sustained learning activities.

## 7. Power and session reliability

- [ ] **E0121** — Check graceful shutdown on each supported machine.
- [ ] **E0122** — Check restart on each supported machine.
- [ ] **E0123** — Check suspend and resume on each supported machine.
- [ ] **E0124** — Check display-only sleep without system suspension.
- [ ] **E0125** — Handle failed shutdown requests visibly.
- [ ] **E0126** — Prevent duplicate shutdown requests while one is pending.
- [ ] **E0127** — Test shutdown when an activity has unsaved work.
- [ ] **E0128** — Warn before a laptop battery becomes critically low.
- [ ] **E0129** — Handle power loss without corrupting launcher preferences.
- [ ] **E0130** — Restore a usable session after an interrupted login.
- [ ] **E0131** — Detect a launcher process that exits unexpectedly.
- [ ] **E0132** — Define bounded launcher restart attempts.
- [ ] **E0133** — Show adult recovery guidance after repeated launcher crashes.
- [ ] **E0134** — Prevent an app crash from terminating the whole child session.
- [ ] **E0135** — Avoid leaving orphaned activity processes after logout.
- [ ] **E0136** — Clean temporary child-session files after logout.
- [ ] **E0137** — Verify session environment variables are available to approved apps.
- [ ] **E0138** — Test a session after the disk becomes nearly full.
- [ ] **E0139** — Test user-session startup with networking disconnected.
- [ ] **E0140** — Confirm no installation-only service blocker remains installed.

## 8. Accounts and authentication

- [ ] **E0141** — Explain the difference between adult and child accounts.
- [ ] **E0142** — Require a usable adult recovery account before child setup ends.
- [ ] **E0143** — Reject duplicate local usernames.
- [ ] **E0144** — Reject usernames already supplied through system identity services.
- [ ] **E0145** — Validate child display names separately from login names.
- [ ] **E0146** — Check password confirmation before account creation.
- [ ] **E0147** — Reject control characters in passwords.
- [ ] **E0148** — Keep passwords out of process arguments.
- [ ] **E0149** — Keep password hashes out of ordinary logs.
- [ ] **E0150** — Verify newly created children are standard users.
- [ ] **E0151** — Verify children are absent from administrative groups.
- [ ] **E0152** — Test changing an adult password.
- [ ] **E0153** — Test changing a child password with adult approval.
- [ ] **E0154** — Test failed account creation without leaving partial accounts.
- [ ] **E0155** — Test rollback failure with a clear recovery message.
- [ ] **E0156** — Support more than one child without sharing private folders.
- [ ] **E0157** — Test account deletion with an explicit data decision.
- [ ] **E0158** — Check that login errors do not reveal password details.
- [ ] **E0159** — Verify locked accounts cannot start child sessions.
- [ ] **E0160** — Document adult recovery when a child forgets a password.

## 9. Adult setup and controls

- [ ] **E0161** — Show the first-run setup action on the adult desktop.
- [ ] **E0162** — Explain that no email address is required for offline setup.
- [ ] **E0163** — Show hardware warnings without blocking unrelated setup steps.
- [ ] **E0164** — Detect live sessions before promising persistent account changes.
- [ ] **E0165** — Offer age-band defaults that adults can review.
- [ ] **E0166** — Let adults choose which home categories appear.
- [ ] **E0167** — Let adults enable or disable individual approved apps.
- [ ] **E0168** — Explain browser availability in plain language.
- [ ] **E0169** — Show which settings require adult authentication.
- [ ] **E0170** — Verify authentication is required for administrative changes.
- [ ] **E0171** — Test cancelling adult authentication cleanly.
- [ ] **E0172** — Separate per-child preferences from system policy.
- [ ] **E0173** — Provide a review screen before saving a child profile.
- [ ] **E0174** — Report failed settings writes without discarding the previous configuration.
- [ ] **E0175** — Offer reset-to-defaults for one child's display preferences.
- [ ] **E0176** — Explain what a preference reset preserves.
- [ ] **E0177** — Show build version in the setup window.
- [ ] **E0178** — Keep setup usable at large text sizes.
- [ ] **E0179** — Make every setup field accessible to assistive tools.
- [ ] **E0180** — Provide an adult checklist after child setup completes.

## 10. Child session boundaries

- [ ] **E0181** — Audit keyboard shortcuts that can open a terminal.
- [ ] **E0182** — Audit keyboard shortcuts that can switch sessions.
- [ ] **E0183** — Audit shortcuts that expose a run-command dialog.
- [ ] **E0184** — Audit desktop context menus in the child session.
- [ ] **E0185** — Audit file chooser access outside the child's home.
- [ ] **E0186** — Audit launchable desktop files outside the approved catalogue.
- [ ] **E0187** — Audit direct Firefox launching outside Eden.
- [ ] **E0188** — Audit URL handlers that launch external programs.
- [ ] **E0189** — Audit whether downloaded executable files can run.
- [ ] **E0190** — Audit permission prompts from approved activities.
- [ ] **E0191** — Test child attempts to install system packages.
- [ ] **E0192** — Test child attempts to edit system policy.
- [ ] **E0193** — Test child access to another child's files.
- [ ] **E0194** — Test child access to adult home directories.
- [ ] **E0195** — Test switching to virtual terminals from the child session.
- [ ] **E0196** — Define the intended boundary between guided interface and enforced restriction.
- [ ] **E0197** — Document known session escape routes honestly.
- [ ] **E0198** — Review removable media permissions for child accounts.
- [ ] **E0199** — Verify child session logout does not expose an adult desktop.
- [ ] **E0200** — Commission a focused security review before describing the session as locked down.

## 11. App launching and catalogue

- [ ] **E0201** — Validate every activity catalogue entry before display.
- [ ] **E0202** — Require a reviewed desktop identifier for each app.
- [ ] **E0203** — Reject catalogue paths supplied by child-controlled files.
- [ ] **E0204** — Check app availability before enabling its tile.
- [ ] **E0205** — Catch desktop-entry constructor failures.
- [ ] **E0206** — Prevent repeated rapid clicks launching duplicate copies.
- [ ] **E0207** — Track actual running activities beyond a fixed cooldown.
- [ ] **E0208** — Bring a running activity to the foreground when selected again.
- [ ] **E0209** — Remove running-state markers when a process exits.
- [ ] **E0210** — Handle apps that spawn a separate child process.
- [ ] **E0211** — Handle single-instance D-Bus applications correctly.
- [ ] **E0212** — Release launch locks when an app fails to start.
- [ ] **E0213** — Show a bounded and reusable error message.
- [ ] **E0214** — Return keyboard focus to a useful control after failure.
- [ ] **E0215** — Define whether two different activities can run together.
- [ ] **E0216** — Record app launch duration without storing child content.
- [ ] **E0217** — Display offline availability for each approved activity.
- [ ] **E0218** — Support adult-defined ordering of approved activity tiles.
- [ ] **E0219** — Show a reviewed age range on the adult app page.
- [ ] **E0220** — Detect broken desktop-file commands during source checks.

## 12. Home screen and navigation

- [ ] **E0221** — Give each home category a distinct accessible icon.
- [ ] **E0222** — Use consistent labels across home and category pages.
- [ ] **E0223** — Keep the Home action in a predictable location.
- [ ] **E0224** — Show a clear selected state for keyboard navigation.
- [ ] **E0225** — Preserve the preferred category when returning from an app.
- [ ] **E0226** — Avoid trapping focus inside the footer.
- [ ] **E0227** — Wrap category tiles on narrow displays.
- [ ] **E0228** — Keep tiles usable at large text scales.
- [ ] **E0229** — Provide a large-pointer preference.
- [ ] **E0230** — Provide an optional reduced-clutter home layout.
- [ ] **E0231** — Offer a small set of adult-selected favourite activities.
- [ ] **E0232** — Explain empty favourites without blaming the child.
- [ ] **E0233** — Make loading states distinguishable from disabled controls.
- [ ] **E0234** — Prevent status text from shifting the entire layout.
- [ ] **E0235** — Keep critical actions visible when content scrolls.
- [ ] **E0236** — Support navigation using only arrow keys and Enter.
- [ ] **E0237** — Provide a visible Back action where appropriate.
- [ ] **E0238** — Use consistent wording for close and return actions.
- [ ] **E0239** — Test long translated category names.
- [ ] **E0240** — Test the home screen with every optional category disabled.

## 13. Visual identity and branding

- [ ] **E0241** — Preserve the approved Eden logo assets.
- [ ] **E0242** — Verify logo aspect ratio at every placement.
- [ ] **E0243** — Use the approved wallpaper set consistently.
- [ ] **E0244** — Define an accessible colour palette for controls.
- [ ] **E0245** — Define a readable default font size.
- [ ] **E0246** — Define spacing rules for launcher tiles.
- [ ] **E0247** — Replace Debian-only welcome text with accurate Eden identification.
- [ ] **E0248** — Keep Debian attribution in an appropriate About page.
- [ ] **E0249** — Show a coherent login-screen theme.
- [ ] **E0250** — Check login contrast against each wallpaper.
- [ ] **E0251** — Provide a plain-background alternative.
- [ ] **E0252** — Avoid decorative animations during loading.
- [ ] **E0253** — Add a monochrome-compatible icon treatment.
- [ ] **E0254** — Document which artwork is original and licensed.
- [ ] **E0255** — Check artwork files for unnecessary size overhead.
- [ ] **E0256** — Provide a modest-resolution asset set for limited hardware.
- [ ] **E0257** — Make branding assets available without network requests.
- [ ] **E0258** — Ensure error screens use the same visual language.
- [ ] **E0259** — Test artwork readability at 1024 by 768.
- [ ] **E0260** — Publish a small style guide for future Eden apps.

## 14. Accessibility foundations

- [ ] **E0261** — Test screen-reader discovery of the home window.
- [ ] **E0262** — Give every interactive tile an accessible name.
- [ ] **E0263** — Give custom controls appropriate accessibility roles.
- [ ] **E0264** — Associate input labels with their fields.
- [ ] **E0265** — Expose toggle states to assistive technology.
- [ ] **E0266** — Announce errors without repeatedly stealing focus.
- [ ] **E0267** — Test keyboard-only adult setup.
- [ ] **E0268** — Test visible focus under high contrast.
- [ ] **E0269** — Test 200-percent text scaling.
- [ ] **E0270** — Test large system cursor settings.
- [ ] **E0271** — Avoid conveying status using colour alone.
- [ ] **E0272** — Provide reduced-motion preferences.
- [ ] **E0273** — Check flashing content against accessibility guidance.
- [ ] **E0274** — Test launcher use with a single-switch input method.
- [ ] **E0275** — Test drag alternatives for motor accessibility.
- [ ] **E0276** — Test touch targets on a small touchscreen.
- [ ] **E0277** — Allow activities to mute nonessential sounds.
- [ ] **E0278** — Provide captions for instructional videos.
- [ ] **E0279** — Provide transcripts for spoken instructions.
- [ ] **E0280** — Record accessibility limitations for each approved app.

## 15. Language and reading accessibility

- [ ] **E0281** — Separate interface strings from application logic.
- [ ] **E0282** — Establish an English UK source translation.
- [ ] **E0283** — Define a translation review process.
- [ ] **E0284** — Add a Welsh interface translation candidate.
- [ ] **E0285** — Add a Polish interface translation candidate.
- [ ] **E0286** — Add an Urdu interface translation candidate.
- [ ] **E0287** — Add an Arabic interface translation candidate.
- [ ] **E0288** — Test right-to-left layout in a supported prototype.
- [ ] **E0289** — Support fonts covering the selected languages.
- [ ] **E0290** — Avoid text embedded inside button artwork.
- [ ] **E0291** — Allow adult choice of spoken-instruction language.
- [ ] **E0292** — Provide optional plain-language labels.
- [ ] **E0293** — Provide a dyslexia-friendly reading layout option without medical claims.
- [ ] **E0294** — Let users adjust reading line spacing.
- [ ] **E0295** — Let users adjust letter spacing in Eden reading apps.
- [ ] **E0296** — Let users choose a warm or cool reading background.
- [ ] **E0297** — Provide pronunciation recordings with clear licensing.
- [ ] **E0298** — Review region-specific spelling in learning content.
- [ ] **E0299** — Review translated safety and consent text with fluent speakers.
- [ ] **E0300** — Test switching language without losing saved child work.

## 16. Local data and privacy

- [ ] **E0301** — Inventory every file written by Eden components.
- [ ] **E0302** — Define separate folders for work and preferences.
- [ ] **E0303** — Keep optional progress storage disabled until explained.
- [ ] **E0304** — Explain local progress data to adults.
- [ ] **E0305** — Offer progress deletion for one child.
- [ ] **E0306** — Verify progress deletion does not erase creative work.
- [ ] **E0307** — Limit permissions on child progress files.
- [ ] **E0308** — Avoid recording unnecessary birth dates.
- [ ] **E0309** — Avoid storing browsing history in launcher telemetry.
- [ ] **E0310** — Remove personal identifiers from support exports by default.
- [ ] **E0311** — Provide a preview before exporting diagnostic information.
- [ ] **E0312** — Make crash logs exclude password fields.
- [ ] **E0313** — Define local log size limits.
- [ ] **E0314** — Rotate old nonessential logs.
- [ ] **E0315** — Document all outbound connections in the default installation.
- [ ] **E0316** — Verify launcher operation without any account on an external service.
- [ ] **E0317** — Avoid third-party trackers in bundled help pages.
- [ ] **E0318** — Review clipboard retention in child sessions.
- [ ] **E0319** — Clear temporary recordings after cancelled microphone activities.
- [ ] **E0320** — Document a data-retention policy adults can understand.

## 17. Browser and web access

- [ ] **E0321** — Keep child web access disabled until explicitly configured.
- [ ] **E0322** — Validate browser policies before enabling the web tile.
- [ ] **E0323** — Show adults which policy file is active.
- [ ] **E0324** — Test each allowed site on the current policy.
- [ ] **E0325** — Test blocked sites from the address bar.
- [ ] **E0326** — Test redirects from allowed to blocked sites.
- [ ] **E0327** — Test search-engine result links.
- [ ] **E0328** — Test embedded videos hosted on third-party domains.
- [ ] **E0329** — Test external protocol handlers from allowed pages.
- [ ] **E0330** — Test opening new browser windows.
- [ ] **E0331** — Test private-browsing policy behaviour.
- [ ] **E0332** — Test downloads from allowed domains.
- [ ] **E0333** — Test extension installation restrictions.
- [ ] **E0334** — Test browser preference pages accessible to children.
- [ ] **E0335** — Test browser invocation from outside Eden.
- [ ] **E0336** — Document limitations of domain allowlists.
- [ ] **E0337** — Review allowlist exceptions for unnecessary breadth.
- [ ] **E0338** — Provide an adult-maintained site list with descriptions.
- [ ] **E0339** — Recheck policies after browser upgrades.
- [ ] **E0340** — Show an understandable offline message when a site cannot load.

## 18. Connectivity and peripherals

- [ ] **E0341** — Show whether the device is offline without alarming the child.
- [ ] **E0342** — Keep local activities available during network loss.
- [ ] **E0343** — Provide adult-only Wi-Fi management.
- [ ] **E0344** — Explain Ethernet as a setup fallback.
- [ ] **E0345** — Test a network with a captive portal.
- [ ] **E0346** — Test correct time after an offline boot.
- [ ] **E0347** — Handle DNS failure separately from missing connectivity.
- [ ] **E0348** — Detect a metered connection before large downloads.
- [ ] **E0349** — Allow adult cancellation of content-pack downloads.
- [ ] **E0350** — Resume interrupted content downloads safely.
- [ ] **E0351** — Verify downloaded content before activation.
- [ ] **E0352** — Define supported USB printer discovery.
- [ ] **E0353** — Test printing a child drawing with adult permission.
- [ ] **E0354** — Test a printer that is temporarily offline.
- [ ] **E0355** — Test removable USB import using approved file types.
- [ ] **E0356** — Test safe removal of imported USB storage.
- [ ] **E0357** — Prevent removable media autorun.
- [ ] **E0358** — Provide Bluetooth disconnect recovery guidance.
- [ ] **E0359** — Test headphones with separate volume settings.
- [ ] **E0360** — Document which peripherals need extra firmware.

## 19. Performance and storage

- [ ] **E0361** — Measure installed size after first setup.
- [ ] **E0362** — Measure size after all default activities are added.
- [ ] **E0363** — Measure idle RAM on a 4 GB device.
- [ ] **E0364** — Measure launcher RAM after repeated navigation.
- [ ] **E0365** — Measure Tux Paint startup on the target SSD.
- [ ] **E0366** — Measure software-rendering CPU use on the iMac.
- [ ] **E0367** — Measure login latency without networking.
- [ ] **E0368** — Set a documented minimum free-space threshold.
- [ ] **E0369** — Warn adults before downloads exceed available space.
- [ ] **E0370** — Measure image-cache growth over a week.
- [ ] **E0371** — Bound thumbnail cache size.
- [ ] **E0372** — Remove abandoned partial download files.
- [ ] **E0373** — Verify progress writes are small and atomic.
- [ ] **E0374** — Avoid polling hardware more often than needed.
- [ ] **E0375** — Measure boot-service timing before optimising it.
- [ ] **E0376** — Test use on a 32 GB storage target.
- [ ] **E0377** — Test use on a slow USB drive as a live session.
- [ ] **E0378** — Check swap behaviour under memory pressure.
- [ ] **E0379** — Test low-memory activity termination recovery.
- [ ] **E0380** — Publish measured requirements rather than guessed specifications.

## 20. Updates and package management

- [ ] **E0381** — Define a supported Debian release for each Eden version.
- [ ] **E0382** — Separate security updates from feature releases.
- [ ] **E0383** — Show adults what an update changes.
- [ ] **E0384** — Require adult approval before installing optional apps.
- [ ] **E0385** — Avoid disruptive updates during a child activity.
- [ ] **E0386** — Check free space before package installation.
- [ ] **E0387** — Check power availability before a large update.
- [ ] **E0388** — Handle an interrupted apt transaction.
- [ ] **E0389** — Detect package-manager lock contention.
- [ ] **E0390** — Provide a recovery command for an incomplete package configuration.
- [ ] **E0391** — Verify launcher startup after GTK updates.
- [ ] **E0392** — Verify child setup after AccountsService updates.
- [ ] **E0393** — Verify browser restrictions after Firefox updates.
- [ ] **E0394** — Verify boot after kernel updates.
- [ ] **E0395** — Keep a versioned copy of system policy before updates.
- [ ] **E0396** — Record installed package versions in release evidence.
- [ ] **E0397** — Test downgrading an Eden-only application package.
- [ ] **E0398** — Define how unsupported releases are retired.
- [ ] **E0399** — Offer a clear restart-needed message.
- [ ] **E0400** — Document an offline update option for restricted networks.

## 21. Backup and restoration

- [ ] **E0401** — Choose which child work folders are backed up.
- [ ] **E0402** — Choose whether local progress is included in backups.
- [ ] **E0403** — Exclude caches and temporary files from backups.
- [ ] **E0404** — Explain backup size before starting.
- [ ] **E0405** — Provide a backup destination picker restricted to adults.
- [ ] **E0406** — Check backup destination space.
- [ ] **E0407** — Verify completed backup archives.
- [ ] **E0408** — Test restoring one child drawing.
- [ ] **E0409** — Test restoring a complete child profile.
- [ ] **E0410** — Test restoring app preferences separately from system policy.
- [ ] **E0411** — Preserve ownership when restoring files.
- [ ] **E0412** — Handle a backup disk removed mid-operation.
- [ ] **E0413** — Reject corrupt backup archives.
- [ ] **E0414** — Avoid overwriting newer work without a clear decision.
- [ ] **E0415** — Support an encrypted backup option for adults.
- [ ] **E0416** — Explain how to keep the backup passphrase recoverable.
- [ ] **E0417** — Document full-disk recovery from a known image.
- [ ] **E0418** — Test restoring on different supported hardware.
- [ ] **E0419** — Record the date of the last successful backup.
- [ ] **E0420** — Provide a printed recovery checklist.

## 22. Diagnostics and support

- [ ] **E0421** — Show model, memory, and build information locally.
- [ ] **E0422** — Show graphics driver and firmware status in an adult report.
- [ ] **E0423** — Detect missing graphical-device nodes.
- [ ] **E0424** — Report whether the current boot uses nomodeset.
- [ ] **E0425** — R…1818 tokens truncated…may be disabled.
- [ ] **E0530** — Explain how to adjust volume.
- [ ] **E0531** — Explain how to adjust text size.
- [ ] **E0532** — Explain how to switch to high contrast.
- [ ] **E0533** — Explain how to print a drawing.
- [ ] **E0534** — Explain how to import an approved content pack.
- [ ] **E0535** — Explain how to remove an optional activity.
- [ ] **E0536** — Explain how to back up child work.
- [ ] **E0537** — Explain how to report an error without sharing passwords.
- [ ] **E0538** — Provide instructions for keyboards missing common symbols.
- [ ] **E0539** — Provide installation instructions that avoid ambiguous disk names.
- [ ] **E0540** — Keep documentation aligned with the actual released interface.

## 28. Content governance and licensing

- [ ] **E0541** — Record the licence of every bundled application.
- [ ] **E0542** — Record the licence of every bundled font.
- [ ] **E0543** — Record attribution requirements for wallpaper assets.
- [ ] **E0544** — Record attribution requirements for sound assets.
- [ ] **E0545** — Review stories for redistribution rights.
- [ ] **E0546** — Review image packs for redistribution rights.
- [ ] **E0547** — Avoid bundling copyrighted film or television material without permission.
- [ ] **E0548** — Create an offline credits page.
- [ ] **E0549** — Track content-pack version and author.
- [ ] **E0550** — Define a content-review checklist for age suitability.
- [ ] **E0551** — Define a content-review checklist for accessibility.
- [ ] **E0552** — Define a content-review checklist for unexpected external links.
- [ ] **E0553** — Record whether an app contains purchases or advertising.
- [ ] **E0554** — Record whether an app requires an online account.
- [ ] **E0555** — Review translated content separately from interface translations.
- [ ] **E0556** — Provide a method for reporting unsuitable bundled content.
- [ ] **E0557** — Define how an app can be removed from the approved catalogue.
- [ ] **E0558** — Check update sources for abandoned applications.
- [ ] **E0559** — Document licence obligations for modified third-party apps.
- [ ] **E0560** — Keep app inclusion decisions separate from candidate suggestions.

## 29. App distribution and optional packs

- [ ] **E0561** — Define a minimal default app set.
- [ ] **E0562** — Define an optional literacy pack.
- [ ] **E0563** — Define an optional numeracy pack.
- [ ] **E0564** — Define an optional creative pack.
- [ ] **E0565** — Define an optional science pack.
- [ ] **E0566** — Define an optional puzzle pack.
- [ ] **E0567** — Show download and installed sizes before adding a pack.
- [ ] **E0568** — Show pack prerequisites before installation.
- [ ] **E0569** — Allow adults to preview included activities.
- [ ] **E0570** — Avoid duplicate copies of shared dependencies.
- [ ] **E0571** — Keep optional packs removable.
- [ ] **E0572** — Preserve child work when removing a pack.
- [ ] **E0573** — Verify pack manifests before installation.
- [ ] **E0574** — Reject a pack with unsupported app identifiers.
- [ ] **E0575** — Support offline pack import from USB.
- [ ] **E0576** — Show when an offline pack requires newer Eden software.
- [ ] **E0577** — Provide rollback for an incomplete pack activation.
- [ ] **E0578** — Keep the child launcher responsive during adult installations.
- [ ] **E0579** — Explain software licences in each pack's adult details.
- [ ] **E0580** — Test a minimal installation without any optional pack.

## 30. Pilot feedback and project tracking

- [ ] **E0581** — Create a hardware issue template.
- [ ] **E0582** — Create a launcher issue template.
- [ ] **E0583** — Create an activity-content issue template.
- [ ] **E0584** — Create an accessibility issue template.
- [ ] **E0585** — Create a privacy issue reporting route.
- [ ] **E0586** — Define how adult testers submit feedback.
- [ ] **E0587** — Avoid collecting child names in bug reports.
- [ ] **E0588** — Track each confirmed blocker with reproduction steps.
- [ ] **E0589** — Separate feature requests from release blockers.
- [ ] **E0590** — Link changes to the evidence that verifies them.
- [ ] **E0591** — Record when a proposed task is already implemented.
- [ ] **E0592** — Retain original roadmap IDs when importing work into issues.
- [ ] **E0593** — Assign priority before estimating large app projects.
- [ ] **E0594** — Estimate storage and maintenance cost for each candidate app.
- [ ] **E0595** — Identify tasks requiring physical hardware access.
- [ ] **E0596** — Identify tasks requiring a fluent language reviewer.
- [ ] **E0597** — Identify tasks requiring an accessibility reviewer.
- [ ] **E0598** — Review the backlog for duplicated or obsolete tasks.
- [ ] **E0599** — Publish a small current milestone instead of promising all features at once.
- [ ] **E0600** — Schedule a release readiness review after the pilot tests.

## 31. Existing app candidates: early learning

- [ ] **E0601** — Review GCompris for the youngest supported age band.
- [ ] **E0602** — Measure GCompris installed size on the target system.
- [ ] **E0603** — Test GCompris startup with software rendering.
- [ ] **E0604** — Verify GCompris activities work without network access.
- [ ] **E0605** — Review GCompris spoken instructions for the chosen language.
- [ ] **E0606** — Map approved GCompris activities to Eden categories.
- [ ] **E0607** — Review GCompris exit behaviour inside the child session.
- [ ] **E0608** — Test GCompris scaling on the iMac display.
- [ ] **E0609** — Review KTuberling for picture-building activities.
- [ ] **E0610** — Test KTuberling spoken labels offline.
- [ ] **E0611** — Review KTuberling asset redistribution requirements.
- [ ] **E0612** — Test KTuberling pointer-only use.
- [ ] **E0613** — Review KLettres for alphabet practice.
- [ ] **E0614** — Check KLettres language-data availability.
- [ ] **E0615** — Test KLettres audio volume controls.
- [ ] **E0616** — Review Blinken for sequence-memory practice.
- [ ] **E0617** — Test Blinken without colour-only cues.
- [ ] **E0618** — Review whether standalone activities duplicate the GCompris pack.
- [ ] **E0619** — Select a small early-learning pilot pack after review.
- [ ] **E0620** — Publish adult guidance for the approved early-learning pack.

## 32. Existing app candidates: literacy

- [ ] **E0621** — Review Kanagram for word-reordering activities.
- [ ] **E0622** — Review Kanagram vocabulary suitability by age band.
- [ ] **E0623** — Test Kanagram dictionary availability offline.
- [ ] **E0624** — Review KHangMan for reading practice and visual presentation.
- [ ] **E0625** — Assess a non-punitive alternative to hangman imagery.
- [ ] **E0626** — Review WordQuiz for locally authored flashcards.
- [ ] **E0627** — Test WordQuiz import of adult-created vocabulary.
- [ ] **E0628** — Review Parley for older-child vocabulary practice.
- [ ] **E0629** — Test Parley without external account requirements.
- [ ] **E0630** — Review Artikulate for pronunciation practice.
- [ ] **E0631** — Review pronunciation-content download sizes.
- [ ] **E0632** — Review Arianna for reading locally supplied ebooks.
- [ ] **E0633** — Test Arianna keyboard navigation.
- [ ] **E0634** — Review Okular for offline illustrated worksheets.
- [ ] **E0635** — Test Okular without exposing unrestricted file browsing.
- [ ] **E0636** — Compare ebook tools for adjustable text and page layout.
- [ ] **E0637** — Check accessibility of locally licensed EPUB content.
- [ ] **E0638** — Check whether candidate readers remember the last page per child.
- [ ] **E0639** — Select one reader for the pilot instead of shipping several.
- [ ] **E0640** — Create a reviewed starter reading pack with clear rights.

## 33. Existing app candidates: numeracy

- [ ] **E0641** — Review KBruch for fractions.
- [ ] **E0642** — Test KBruch difficulty settings with adult supervision.
- [ ] **E0643** — Review KAlgebra for older learners.
- [ ] **E0644** — Review KAlgebra help content for offline availability.
- [ ] **E0645** — Review Kig for interactive geometry.
- [ ] **E0646** — Test Kig on a modest-resolution display.
- [ ] **E0647** — Review KmPlot for graph exploration by older learners.
- [ ] **E0648** — Review KCalc as an optional adult-approved calculator.
- [ ] **E0649** — Compare calculator input accessibility.
- [ ] **E0650** — Review GCompris counting activities separately from advanced maths.
- [ ] **E0651** — Review GCompris arithmetic activities for UK terminology.
- [ ] **E0652** — Test maths symbols with screen-reader output.
- [ ] **E0653** — Check candidate maths apps for unexpected network links.
- [ ] **E0654** — Measure additional Qt dependencies for maths candidates.
- [ ] **E0655** — Review whether numeric answer fields accept local decimal conventions.
- [ ] **E0656** — Check saved worksheet formats for portability.
- [ ] **E0657** — Test candidate maths apps under large text.
- [ ] **E0658** — Select numeracy activities appropriate for distinct age bands.
- [ ] **E0659** — Write adult descriptions that explain the skill practised.
- [ ] **E0660** — Publish a pilot numeracy pack after acceptance tests.

## 34. Existing app candidates: typing and coding

- [ ] **E0661** — Review KTouch for touch-typing practice.
- [ ] **E0662** — Check KTouch UK keyboard lessons.
- [ ] **E0663** — Test KTouch on a compact keyboard.
- [ ] **E0664** — Review KTouch progress storage permissions.
- [ ] **E0665** — Review KTurtle for introductory programming.
- [ ] **E0666** — Test KTurtle examples without internet access.
- [ ] **E0667** — Review KTurtle interface complexity for beginners.
- [ ] **E0668** — Review Rocs for older-child graph exploration.
- [ ] **E0669** — Review Rocs scripting exposure before child-session inclusion.
- [ ] **E0670** — Research a maintained offline block-coding editor.
- [ ] **E0671** — Check the chosen block editor's packaging and redistribution rights.
- [ ] **E0672** — Check whether the block editor opens external websites.
- [ ] **E0673** — Test a block project saved in the child's work folder.
- [ ] **E0674** — Test loading a local project without code execution outside its sandbox.
- [ ] **E0675** — Research an offline Python learning environment for older children.
- [ ] **E0676** — Define what permissions beginner coding activities may receive.
- [ ] **E0677** — Avoid giving coding apps unrestricted administrative access.
- [ ] **E0678** — Test lesson reset without deleting the child's own projects.
- [ ] **E0679** — Compare the maintenance burden of existing coding tools.
- [ ] **E0680** — Select one beginner coding path for a limited pilot.

## 35. Existing app candidates: drawing and making

- [ ] **E0681** — Recheck the currently included Tux Paint on the installed iMac.
- [ ] **E0682** — Test Tux Paint save and reopen behaviour per child.
- [ ] **E0683** — Review Tux Paint stamp packs and their licences.
- [ ] **E0684** — Test Tux Paint with reduced sound effects.
- [ ] **E0685** — Test Tux Paint printing controls.
- [ ] **E0686** — Review KolourPaint for older children.
- [ ] **E0687** — Compare KolourPaint controls with Eden's accessibility goals.
- [ ] **E0688** — Review Krita as an optional advanced art tool.
- [ ] **E0689** — Measure Krita disk and RAM requirements before inclusion.
- [ ] **E0690** — Test Krita using software rendering where supported.
- [ ] **E0691** — Review Karbon for optional vector drawing.
- [ ] **E0692** — Review Glaxnimate for optional animation projects.
- [ ] **E0693** — Test animation export without network services.
- [ ] **E0694** — Review Peruse Comic Book Creator for story projects.
- [ ] **E0695** — Check comic export formats and reader compatibility.
- [ ] **E0696** — Review Skanlite for adult-assisted artwork scanning.
- [ ] **E0697** — Require approval before scanners import content into child folders.
- [ ] **E0698** — Compare drawing apps to avoid overlapping defaults.
- [ ] **E0699** — Choose a small approved creative pack.
- [ ] **E0700** — Document how children retain artwork if an app is removed.

## 36. Existing app candidates: music and media

- [ ] **E0701** — Review Minuet for music education.
- [ ] **E0702** — Check Minuet's instrument and sound dependencies.
- [ ] **E0703** — Review Kwave for optional sound editing.
- [ ] **E0704** — Check Kwave recording controls for clear consent.
- [ ] **E0705** — Review a maintained simple offline audio player.
- [ ] **E0706** — Test local audio playback with no browsing features exposed.
- [ ] **E0707** — Review Dragon Player for adult-supplied videos.
- [ ] **E0708** — Test captions in the candidate video player.
- [ ] **E0709** — Review Haruna as an alternative local video player.
- [ ] **E0710** — Compare media-player file chooser exposure.
- [ ] **E0711** — Review Kamoso for optional adult-enabled camera use.
- [ ] **E0712** — Test the camera activity without uploading images.
- [ ] **E0713** — Review an offline metronome candidate.
- [ ] **E0714** — Review an offline virtual piano candidate.
- [ ] **E0715** — Measure sound-library download sizes.
- [ ] **E0716** — Check multimedia codecs required by licensed sample files.
- [ ] **E0717** — Verify no app silently enables microphone recording.
- [ ] **E0718** — Choose one media player for the default pack.
- [ ] **E0719** — Write guidance for importing family-owned media legally.
- [ ] **E0720** — Test separate volume preferences for creative and instructional sounds.

## 37. Existing app candidates: geography and science

- [ ] **E0721** — Review Marble for a local globe activity.
- [ ] **E0722** — Check which Marble maps remain useful offline.
- [ ] **E0723** — Review KGeography for geography practice.
- [ ] **E0724** — Review map labels for age suitability and disputed-boundary presentation.
- [ ] **E0725** — Review KStars for optional astronomy exploration.
- [ ] **E0726** — Measure KStars data-pack size.
- [ ] **E0727** — Test KStars without location permissions.
- [ ] **E0728** — Review Kalzium for older-child chemistry exploration.
- [ ] **E0729** — Review Kalzium content for age-appropriate presentation.
- [ ] **E0730** — Review Step for optional physics demonstrations.
- [ ] **E0731** — Test Step performance on the iMac.
- [ ] **E0732** — Review KAtomic for molecule-themed puzzles.
- [ ] **E0733** — Avoid describing KAtomic puzzles as a complete chemistry curriculum.
- [ ] **E0734** — Review an offline nature-identification reference candidate.
- [ ] **E0735** — Check nature-reference image licences.
- [ ] **E0736** — Review an offline periodic-table alternative.
- [ ] **E0737** — Compare science tools for unnecessary interface complexity.
- [ ] **E0738** — Select a small offline science pilot pack.
- [ ] **E0739** — Provide adult notes for experiments that require supervision.
- [ ] **E0740** — Test science pack launchers without administrative privileges.

## 38. Existing app candidates: puzzles and board games

- [ ] **E0741** — Review Palapeli for jigsaw puzzles.
- [ ] **E0742** — Review Palapeli image-pack rights.
- [ ] **E0743** — Test Palapeli without requiring precise dragging.
- [ ] **E0744** — Review KSudoku for number logic.
- [ ] **E0745** — Test KSudoku difficulty labels.
- [ ] **E0746** — Review KFourInLine for local two-player play.
- [ ] **E0747** — Review KReversi for local board play.
- [ ] **E0748** — Review KSquares for turn-taking activities.
- [ ] **E0749** — Review Picmi for picture-logic puzzles.
- [ ] **E0750** — Review KNetWalk for connection puzzles.
- [ ] **E0751** — Review Kubrick for optional spatial puzzles.
- [ ] **E0752** — Test Kubrick motion settings.
- [ ] **E0753** — Review KBlackbox for older-child deduction puzzles.
- [ ] **E0754** — Review Bovo for local strategy play.
- [ ] **E0755** — Review KJumpingCube for simple turn-based play.
- [ ] **E0756** — Review KShisen for accessible tile matching.
- [ ] **E0757** — Test game audio mute controls.
- [ ] **E0758** — Check games for external scoreboards or network modes.
- [ ] **E0759** — Select puzzle candidates by distinct learning value.
- [ ] **E0760** — Create a reviewed puzzle pack with optional hints.

## 39. Existing app candidates: accessible utilities

- [ ] **E0761** — Review KMag as an adult-enabled magnifier.
- [ ] **E0762** — Test KMag interaction with the Eden fullscreen launcher.
- [ ] **E0763** — Review KMouth for an optional speech-output utility.
- [ ] **E0764** — Review speech-voice availability without internet.
- [ ] **E0765** — Review KMouseTool for users who need automatic clicking.
- [ ] **E0766** — Test accidental-click prevention with automatic clicking enabled.
- [ ] **E0767** — Review Kontrast for adult contrast checking.
- [ ] **E0768** — Review a maintained on-screen keyboard candidate.
- [ ] **E0769** — Test on-screen keyboard access at graphical login.
- [ ] **E0770** — Test on-screen keyboard access in Eden setup.
- [ ] **E0771** — Review a maintained screen reader compatible with the desktop.
- [ ] **E0772** — Test reading launcher names using the selected screen reader.
- [ ] **E0773** — Review a simple document viewer for adult help files.
- [ ] **E0774** — Review a file manager configuration restricted to child work.
- [ ] **E0775** — Review an archive tool for adult-managed content imports.
- [ ] **E0776** — Check utility shortcuts cannot bypass intended child restrictions.
- [ ] **E0777** — Measure the footprint of accessibility support packages.
- [ ] **E0778** — Write instructions for enabling assistive tools without a mouse.
- [ ] **E0779** — Select utilities based on actual tester needs.
- [ ] **E0780** — Document assistive-tool combinations that have been tested.

## 40. Existing app candidates: adult and classroom tools

- [ ] **E0781** — Review GCompris-teachers as an optional classroom companion.
- [ ] **E0782** — Check whether classroom tools need a network service.
- [ ] **E0783** — Review KBackup for an adult-only backup interface.
- [ ] **E0784** — Compare its restore workflow with Eden recovery requirements.
- [ ] **E0785** — Review KOrganizer for optional adult-managed schedules.
- [ ] **E0786** — Review a simple offline PDF worksheet tool.
- [ ] **E0787** — Review LibreOffice as an optional older-child and adult package.
- [ ] **E0788** — Measure the full office-suite footprint before proposing inclusion.
- [ ] **E0789** — Compare a single word processor with the full office suite.
- [ ] **E0790** — Review an offline presentation tool for school projects.
- [ ] **E0791** — Review printing utilities with adult confirmation.
- [ ] **E0792** — Review a local screenshot utility for support reports.
- [ ] **E0793** — Ensure support screenshots require an explicit capture action.
- [ ] **E0794** — Review a disk-usage viewer restricted to adult sessions.
- [ ] **E0795** — Review a simple file checksum utility for ISO verification.
- [ ] **E0796** — Review an adult software manager with a small approved catalogue.
- [ ] **E0797** — Ensure software-manager installation requests require authentication.
- [ ] **E0798** — Compare candidate classroom tools against home-use requirements.
- [ ] **E0799** — Select which adult tools belong outside the child launcher.
- [ ] **E0800** — Publish the final candidate review decisions and rejected alternatives.

## 41. Build Eden Story Garden

- [ ] **E0801** — Define the scope of an offline illustrated story reader.
- [ ] **E0802** — Create a library screen for adult-approved story packs.
- [ ] **E0803** — Provide adjustable font size within stories.
- [ ] **E0804** — Provide adjustable line spacing within stories.
- [ ] **E0805** — Offer a distraction-reduced reading view.
- [ ] **E0806** — Implement chapter navigation with keyboard support.
- [ ] **E0807** — Remember the last page separately for each child.
- [ ] **E0808** — Add optional word highlighting for recorded narration.
- [ ] **E0809** — Allow narration speed adjustment without changing pitch where supported.
- [ ] **E0810** — Provide a simple bookmark action.
- [ ] **E0811** — Add a local favourites shelf.
- [ ] **E0812** — Let adults import a licensed story pack.
- [ ] **E0813** — Validate story-pack paths against directory traversal.
- [ ] **E0814** — Reject external links in offline story content by default.
- [ ] **E0815** — Show story author and licence information.
- [ ] **E0816** — Support image descriptions for illustrated pages.
- [ ] **E0817** — Add optional gentle comprehension prompts.
- [ ] **E0818** — Make prompts skippable without penalties.
- [ ] **E0819** — Provide a licensed sample story pack.
- [ ] **E0820** — Test the reader on basic-graphics hardware.

## 42. Build Eden Number Meadow

- [ ] **E0821** — Define a small offline numeracy activity engine.
- [ ] **E0822** — Build counting objects from one to ten.
- [ ] **E0823** — Build counting objects from eleven to twenty.
- [ ] **E0824** — Build number-to-quantity matching.
- [ ] **E0825** — Build quantity comparison without timed scoring.
- [ ] **E0826** — Build number ordering on a visual line.
- [ ] **E0827** — Build simple addition using movable objects.
- [ ] **E0828** — Build simple subtraction using removable objects.
- [ ] **E0829** — Build number bonds to ten.
- [ ] **E0830** — Build tens-and-ones grouping.
- [ ] **E0831** — Build skip-counting sequences.
- [ ] **E0832** — Build multiplication as equal groups.
- [ ] **E0833** — Build division as equal sharing.
- [ ] **E0834** — Build halves and quarters with visual shapes.
- [ ] **E0835** — Build a UK coins counting activity using reviewed artwork.
- [ ] **E0836** — Add optional spoken instructions.
- [ ] **E0837** — Allow an adult to choose a starting difficulty.
- [ ] **E0838** — Offer hints before presenting another problem.
- [ ] **E0839** — Save optional local practice progress.
- [ ] **E0840** — Test all activities without colour-dependent answers.

## 43. Build Eden Word Woodland

- [ ] **E0841** — Define an offline phonics-content format.
- [ ] **E0842** — Create sound-to-letter matching.
- [ ] **E0843** — Create beginning-sound sorting.
- [ ] **E0844** — Create ending-sound matching.
- [ ] **E0845** — Create letter-shape recognition.
- [ ] **E0846** — Create uppercase-to-lowercase matching.
- [ ] **E0847** — Create consonant-vowel-consonant blending.
- [ ] **E0848** — Create word-to-picture matching.
- [ ] **E0849** — Create simple rhyme matching.
- [ ] **E0850** — Create syllable clapping with a non-microphone input option.
- [ ] **E0851** — Create missing-letter word completion.
- [ ] **E0852** — Create sentence ordering with short illustrated sentences.
- [ ] **E0853** — Create a personal practice-word list for adults.
- [ ] **E0854** — Allow accent-specific recordings selected by adults.
- [ ] **E0855** — Review pronunciation recordings with literacy specialists.
- [ ] **E0856** — Avoid marking regional pronunciations as inherently wrong.
- [ ] **E0857** — Add large clickable answer targets.
- [ ] **E0858** — Provide audio replay without limiting attempts.
- [ ] **E0859** — Offer a practice mode with no score display.
- [ ] **E0860** — Test the activity set with a licensed starter vocabulary.

## 44. Build Eden Art Studio

- [ ] **E0861** — Define a simple drawing canvas separate from advanced art apps.
- [ ] **E0862** — Create a large brush selector.
- [ ] **E0863** — Create a restrained initial colour palette.
- [ ] **E0864** — Add a shape tool with adjustable outline width.
- [ ] **E0865** — Add fill with bounded region handling.
- [ ] **E0866** — Add undo and redo with a clear history limit.
- [ ] **E0867** — Add a visible save action.
- [ ] **E0868** — Autosave unfinished drawings locally.
- [ ] **E0869** — Provide a gallery of the child's own drawings.
- [ ] **E0870** — Allow renaming artwork with a simple title field.
- [ ] **E0871** — Export to a standard PNG file.
- [ ] **E0872** — Provide a printable page layout preview.
- [ ] **E0873** — Add a symmetry drawing mode.
- [ ] **E0874** — Add a reusable stencil mode.
- [ ] **E0875** — Add an original licensed sticker library.
- [ ] **E0876** — Provide a keyboard alternative to pointer dragging.
- [ ] **E0877** — Add canvas zoom without hiding core controls.
- [ ] **E0878** — Warn gently before discarding unsaved work.
- [ ] **E0879** — Handle full-disk saves without destroying the previous file.
- [ ] **E0880** — Test artwork export in another standard image viewer.

## 45. Build Eden Music Grove

- [ ] **E0881** — Define a simple offline music-making workspace.
- [ ] **E0882** — Create a playable one-octave keyboard.
- [ ] **E0883** — Add an alternative large-button note layout.
- [ ] **E0884** — Create a step sequencer with a small grid.
- [ ] **E0885** — Add percussion tracks with original samples.
- [ ] **E0886** — Let children adjust tempo within a safe useful range.
- [ ] **E0887** — Add a visual metronome.
- [ ] **E0888** — Provide a mute button that always remains visible.
- [ ] **E0889** — Create a rhythm-copy activity.
- [ ] **E0890** — Create high-note and low-note matching.
- [ ] **E0891** — Create instrument-sound identification using licensed samples.
- [ ] **E0892** — Show a simple visual representation of note duration.
- [ ] **E0893** — Allow saving a short composition locally.
- [ ] **E0894** — Allow reopening a saved composition.
- [ ] **E0895** — Export a composition to a standard audio file.
- [ ] **E0896** — Prevent audio clipping in the default mixer.
- [ ] **E0897** — Avoid sudden loud preview sounds.
- [ ] **E0898** — Provide non-audio feedback for beat placement.
- [ ] **E0899** — Create a starter pack of original musical patterns.
- [ ] **E0900** — Test latency on the oldest supported machine.

## 46. Build Eden Puzzle Pond

- [ ] **E0901** — Define a shared offline puzzle framework.
- [ ] **E0902** — Create a large-piece jigsaw activity.
- [ ] **E0903** — Create a picture memory-pairs activity.
- [ ] **E0904** — Create a simple maze activity.
- [ ] **E0905** — Create a path-connection activity.
- [ ] **E0906** — Create a shape-fitting activity.
- [ ] **E0907** — Create a repeating-pattern completion activity.
- [ ] **E0908** — Create a sorting-by-size activity.
- [ ] **E0909** — Create a sorting-by-category activity.
- [ ] **E0910** — Create a sequence-ordering activity.
- [ ] **E0911** — Create a hidden-object picture using original art.
- [ ] **E0912** — Create a non-timed spot-the-difference activity.
- [ ] **E0913** — Create a simple tile-rotation activity.
- [ ] **E0914** — Create a small grid-based logic activity.
- [ ] **E0915** — Add a hint action that never spends tokens.
- [ ] **E0916** — Allow adults to adjust visual complexity.
- [ ] **E0917** — Ensure every generated puzzle has a solution.
- [ ] **E0918** — Restore a puzzle after accidental closing.
- [ ] **E0919** — Provide optional shared-device two-player puzzles.
- [ ] **E0920** — Test puzzles without precision dragging or speed requirements.

## 47. Build Eden Nature Explorer

- [ ] **E0921** — Define an offline nature reference with reviewed content.
- [ ] **E0922** — Create a tree and leaf matching activity.
- [ ] **E0923** — Create an animal and habitat matching activity.
- [ ] **E0924** — Create an animal-track matching activity.
- [ ] **E0925** — Create a seasonal change timeline.
- [ ] **E0926** — Create a simple food-chain activity.
- [ ] **E0927** — Create a seed-to-plant sequence activity.
- [ ] **E0928** — Create a pollinator matching activity.
- [ ] **E0929** — Create a day-and-night animal sorting activity.
- [ ] **E0930** — Create an accessible garden observation journal.
- [ ] **E0931** — Allow a child to draw an observation instead of taking a photo.
- [ ] **E0932** — Allow adult-approved import of a nature photograph.
- [ ] **E0933** — Store observations only on the device by default.
- [ ] **E0934** — Provide a weather-symbol journal without needing live weather.
- [ ] **E0935** — Create a cloud-types illustrated reference.
- [ ] **E0936** — Create a safe outdoor observation checklist.
- [ ] **E0937** — Explain that the app cannot identify edible or safe plants.
- [ ] **E0938** — Add credits for every reference image.
- [ ] **E0939** — Review factual content with an appropriate subject reviewer.
- [ ] **E0940** — Test the full nature pack without a network connection.

## 48. Build Eden Time and Routines

- [ ] **E0941** — Define an adult-managed offline routine board.
- [ ] **E0942** — Create a visual morning routine.
- [ ] **E0943** — Create a visual bedtime routine.
- [ ] **E0944** — Allow adults to reorder routine steps.
- [ ] **E0945** — Allow adults to use original pictograms.
- [ ] **E0946** — Allow a child to mark a step complete.
- [ ] **E0947** — Provide a reversible completion action.
- [ ] **E0948** — Reset routine completion at an adult-selected time.
- [ ] **E0949** — Create an analogue-clock exploration screen.
- [ ] **E0950** — Create digital-to-analogue time matching.
- [ ] **E0951** — Create a days-of-the-week ordering activity.
- [ ] **E0952** — Create a months-and-seasons activity.
- [ ] **E0953** — Provide an optional quiet activity timer.
- [ ] **E0954** — Show a warning before a timer ends.
- [ ] **E0955** — Avoid force-closing unsaved work when time expires.
- [ ] **E0956** — Make sounds optional for all reminders.
- [ ] **E0957** — Display routines without requiring a child's date of birth.
- [ ] **E0958** — Keep the device clock separate from learning-clock controls.
- [ ] **E0959** — Provide a printable routine sheet.
- [ ] **E0960** — Test routines when the device starts with an incorrect clock.

## 49. Build Eden Feelings and Quiet Space

- [ ] **E0961** — Define a non-clinical wellbeing activity scope.
- [ ] **E0962** — Create an optional feelings-selection board.
- [ ] **E0963** — Use respectful labels without inferring a diagnosis.
- [ ] **E0964** — Allow skipping any feelings prompt.
- [ ] **E0965** — Create a quiet drawing space.
- [ ] **E0966** — Create a paced visual breathing animation.
- [ ] **E0967** — Allow breathing animation speed to be adjusted.
- [ ] **E0968** — Provide a static alternative for reduced-motion users.
- [ ] **E0969** — Create an optional calm-sound player using licensed audio.
- [ ] **E0970** — Offer a silent mode with equivalent visual controls.
- [ ] **E0971** — Create a simple grounding observation activity.
- [ ] **E0972** — Create an adult-selected list of comforting activities.
- [ ] **E0973** — Avoid rewards tied to reporting a particular emotion.
- [ ] **E0974** — Avoid asking children to disclose private events.
- [ ] **E0975** — Keep any optional mood notes local.
- [ ] **E0976** — Allow adults to disable mood-history storage entirely.
- [ ] **E0977** — Provide an obvious way to erase a saved note.
- [ ] **E0978** — Make clear that the app is not medical care.
- [ ] **E0979** — Review wording with an appropriate child-wellbeing specialist.
- [ ] **E0980** — Test every activity without recording voice or video.

## 50. Build Eden Maker Lab and personal workspace

- [ ] **E0981** — Define a beginner-friendly offline project workspace.
- [ ] **E0982** — Create a project shelf for drawings stories and compositions.
- [ ] **E0983** — Provide child-owned folders with understandable names.
- [ ] **E0984** — Create a simple comic page builder.
- [ ] **E0985** — Create a postcard and greeting-card maker.
- [ ] **E0986** — Create a stop-motion planner without requiring a camera.
- [ ] **E0987** — Create a frame-by-frame animation prototype.
- [ ] **E0988** — Create an offline pattern-block design activity.
- [ ] **E0989** — Create a beginner command-sequence activity with an animated character.
- [ ] **E0990** — Create a grid-based coding puzzle with undo.
- [ ] **E0991** — Create a local story-sequence builder combining pictures and text.
- [ ] **E0992** — Create a simple project presentation mode.
- [ ] **E0993** — Let adults import only validated project templates.
- [ ] **E0994** — Prevent templates from embedding executable commands.
- [ ] **E0995** — Provide standard export formats for each project type.
- [ ] **E0996** — Show local save status before a child leaves a project.
- [ ] **E0997** — Provide a recycle bin for accidentally deleted child projects.
- [ ] **E0998** — Require adult approval before permanent project deletion.
- [ ] **E0999** — Test restoring an exported project on another Eden device.
- [ ] **E1000** — Choose one Maker Lab prototype for a small pilot before expanding scope.

## Candidate discovery sources

These official catalogues ground the named candidate examples; they do not certify suitability for EdenOS or package availability on its target release. The detailed review and custom-product tasks above are planning proposals.

- [KDE Applications catalogue](https://apps.kde.org/) — named education, creative, puzzle and utility candidates.
- [GCompris](https://gcompris.net/index-en) — educational activity suite.
- [Tux Paint features](https://tuxpaint.org/features/?lang=en_GB) — current included drawing activity and possible pack review.
- [Apps for GNOME](https://apps.gnome.org/en-GB/) — additional utility candidates to research.

Checklist validation: 50 sections × 20 tasks = 1,000 tasks; unique IDs E0001 through E1000; no exact duplicate task text.

## Roadmap extension: picture-based child sign-in

The original 1,000-task checklist is preserved. This requested feature is
tracked as a post-checklist extension because it needs greeter integration and
must not be confused with the current LightDM account flow.

- [ ] **E1001** — Define an adult-only profile editor for a child's display name and picture.
- [ ] **E1002** — Offer a small set of inclusive built-in avatar illustrations before allowing custom images.
- [ ] **E1003** — Store profile pictures in a protected local directory, separate from child home folders.
- [ ] **E1004** — Validate image type, dimensions, file size, and orientation before saving an avatar.
- [ ] **E1005** — Show large picture-and-name tiles for child accounts at the sign-in screen.
- [ ] **E1006** — Make each tile keyboard, touch, switch, and screen-reader accessible.
- [ ] **E1007** — Make selecting a tile choose the matching local account without displaying its username.
- [ ] **E1008** — Keep passwords, hashes, recovery details, and other children's data out of the tile UI.
- [ ] **E1009** — Provide an adult-only fallback for profiles without a picture or with a failed image load.
- [ ] **E1010** — Test multiple children, duplicate display names, locked accounts, and greeter recovery.
- [ ] **E1011** — Verify the picture-based greeter still works in basic graphics mode.
- [ ] **E1012** — Add an adult preview before publishing a profile picture to the greeter.
- [ ] **E1013** — Provide a clear removal/reset action that returns to the default avatar.
- [ ] **E1014** — Document that a picture is a sign-in aid, not an authentication factor.
- [ ] **E1015** — Verify no avatar or display name is uploaded or synchronised online.


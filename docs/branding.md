# EdenOS branding integration

The Garden of Eden artwork pack contains one logo and six 16:9 wallpapers:
`01-eden-sunrise.png`, `02-eden-waterfalls.png`,
`03-eden-rainbow.png`, `04-eden-moonlight.png`,
`05-eden-butterflies.png`, and `06-eden-orchard.png`.

## Preparing the next ISO

1. Download `EdenOS_Artwork_Pack.zip` from the conversation and extract its
   `edenos-artwork` directory into the root of the EdenOS repository.
2. The expected layout is `edenos-artwork/logo/edenos-logo.png` and
   `edenos-artwork/wallpapers/*.png` (exactly six wallpaper files).
3. Commit the artwork directory to the repository (or use a build environment
   where the artwork is already present) **before** triggering GitHub Actions.
4. Run the **Build Eden OS ISO** workflow from the Actions tab.
5. Download the *new* artifact. The old test ISO predates the branding work.

The build invokes `scripts/stage-branding`. When the pack is present it copies
the artwork into `/usr/share/backgrounds/edenos/`, installs the logo in
`/usr/share/pixmaps/`, and configures a sunrise background for the LightDM GTK
greeter and a default XFCE desktop profile.

The image also includes an EdenOS Plymouth theme and quiet `splash` boot
defaults. During a normal boot, Plymouth uses the sunrise wallpaper with the
EdenOS logo centred until LightDM appears. A recovery/text boot entry remains
available for diagnosing graphics failures. The splash can only display the
wallpaper and logo when the branding pack is present.

If artwork is absent, the build explicitly reports that and proceeds without
the theme. This allows ordinary source builds to remain functional but means
**a successful ISO build alone does not prove branding is embedded**.

## Manual acceptance checks

- Confirm all six wallpapers are present after boot.
- Confirm the default background appears on the adult XFCE desktop.
- Confirm the greeter shows the intended background, with legible controls.
- Confirm that the child full-screen Eden launcher is not unintentionally
  obstructed by desktop or login wallpaper settings.
- Test 1024×768, 1366×768 and 1920×1080 displays; test high contrast and
  reduced motion settings.
- Confirm no personal user account or network requirement is bundled into
  the image.

This branding work is for a development ISO. Parent account isolation, browser
restriction and child safety gates still need direct VM/hardware verification.


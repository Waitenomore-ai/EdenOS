# Eden's Garden desktop app — v0.75.0

The desktop app is a lightweight Electron application for Windows, macOS and Linux. It opens the public unified Eden's Garden experience in a dedicated, child-friendly desktop window:

`https://www.edensgarden.uk/app/unified/`

## Installer experience

- **Windows:** branded NSIS setup wizard using the approved original Eden character artwork, custom Eden's Garden header/sidebar artwork, a welcome page, installation-location selection, installation progress and a branded completion page. Desktop and Start Menu shortcuts are created, and the app can launch after setup.
- **macOS:** branded DMG with Eden's Garden background artwork and a drag-to-Applications layout. Both Intel (x64) and Apple silicon (arm64) builds are produced.
- **Linux:** native Debian package (`.deb`) and portable AppImage (`.AppImage`). These use the Eden's Garden application icon and desktop launcher; the standard package manager or AppImage launch flow is used rather than pretending Linux has a Windows-style setup wizard.

The Windows welcome and finish screens contain installation information only. They are **not** a fabricated licence agreement. The installer clearly explains that this is the desktop app, not the full Eden OS operating system.

## Build and validation

Use Node.js 22 in this directory:

```bash
npm ci
npm run check
npm run dist:win
npm run dist:mac
npm run dist:linux
```

`npm run check` validates the Electron entry point and required branded installer assets, including expected image dimensions and NSIS welcome/finish page definitions.

GitHub Actions builds each platform on its matching hosted runner and performs clean-runner install/launch/uninstall smoke tests before uploading short-lived build artifacts. The workflow does not publish a public release automatically.

## Important release limitations

- Windows signing and Apple signing/notarisation are not configured. SmartScreen and Gatekeeper may show warnings.
- The app loads the unified web experience from the internet. It is not a full offline bundle of all learning content or media.
- Browser storage is local to this desktop app; profile and reward data are not synchronized between devices.
- Hosted CI smoke tests are not a substitute for final hands-on testing on real Windows, macOS and Linux devices.
- The existing Eden OS installation on the iMac is separate and is not modified by this desktop packaging project.

## Security

Remote web content runs with Node integration disabled, context isolation and sandboxing enabled. Native permission requests are denied, and links outside the approved unified app origin open in the system browser. Do not expose privileged Electron APIs to the remote website.

Support: hello@edensgarden.uk  
Website: https://edensgarden.uk

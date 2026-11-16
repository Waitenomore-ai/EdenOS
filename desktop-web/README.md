# Eden's Garden desktop shell — build candidate v75

This folder stages a minimal Electron desktop wrapper for the **public unified Eden's Garden web app**.

**Current status:** source and packaging configuration only. The Windows and macOS installers are not signed, notarised, or user-tested. Do not distribute them as a final release until the GitHub Actions builds succeed and they have been tested on those platforms.

## Behaviour

- Loads https://www.edensgarden.uk/app/unified/ in a dedicated desktop window.
- Browser storage is local to the desktop application, preserving child profiles and sticker rewards between launches.
- Story Garden's explicit offline downloads can work after the content has been cached inside the desktop app.
- No Node.js APIs are exposed to remote web content; sandbox, isolation and web security are enabled.
- Requests for native permissions such as microphone, location and notifications are denied.
- Links outside the approved unified app URL open in the default web browser.
- An offline fallback page is displayed only if the web app itself cannot load.

## Build instructions

Use Node.js 22. In this folder:

```bash
npm ci
npm run check
npm run dist:win   # Windows runner only
npm run dist:mac   # macOS runner only
```

The workflow `.github/workflows/desktop-web.yml` can compile unsigned Windows x64 EXE and macOS x64/arm64 DMG files on matching GitHub Actions runners. It uploads build artifacts, **not public releases**.

### Limitations

- Native signing and notarisation are not yet configured. Microsoft SmartScreen and Apple Gatekeeper may warn.
- The app loads web resources from the internet on first use. It is not a standalone full-media bundle.
- Device profiles and rewards remain local; there is no server account sync.
- Accessibility tests, OS packaging tests, SmartScreen and Gatekeeper validation are outstanding.
- The official iMac Eden OS desktop remains separate and untouched.

**Security:** Never enable `nodeIntegration` or permit privileged APIs to run from remote website code.

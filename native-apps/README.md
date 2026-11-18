# Eden native desktop app — isolated development build

**Status: development only; not production ready or deployed.** The iMac Eden OS remains the source of truth. No live iMac or website modifications are authorised by this project.

## Implemented and tested
- Native Qt Widgets app with child selection, approved character avatars, compact 4×2 activity launcher and accessible controls.
- Isolated native profile persistence, parent PIN setup/unlock, Parent Corner profile creation and per-child activity choices; first-run parent onboarding.
- All eight home-screen activities now have native interactions using byte-identical copies of their iMac models. **My Day** runs the approved full-day routine. **Story Garden** now has a 75-book / 762-page **staging** bookshelf recovered from iMac source. Only 12 books are marked original; 63 are explicitly text drafts, not final approved text. 762 recorded MP3 files are staged and wired to Qt Multimedia; 40 staging page PNGs are shown where mapped. Narration playback needs real-device verification. The older preserved 18-book catalogue remains for comparison. **Art Studio** now includes a Qt freehand canvas with 9 colours, drawing undo/redo/clear, PNG save, and four free approved stickers (75 verified sticker PNGs staged; 71 reward-locked). Still missing complete iMac layers, backgrounds, drag positioning and Garden Stars entitlement integration.
- Recovered iMac staging artwork: 96 Word Woodland PNGs, 80 Number Meadow PNGs, plus 11 approved avatars. See `artwork-audit.json` for known gaps. Artwork needs visual approval review.
- Qt offscreen automated tests, including PIN security, profile management, game logic and compact 800×600 layout. These are **not** a substitute for visual and assistive-technology QA.

## Local test

```sh
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -q
.venv/bin/python -m eden_native.qt_app
```

`create_window()` without injected models is a limited preview. Test fixtures inject isolated `ApprovedPinAdapter` and `ProfileRepository`; production wiring remains to be implemented and audited.

## Remaining blockers
1. Approved artwork completeness and final visual comparison, especially 11 missing Word Woodland picture words and two missing Puzzle Pond card pictures.
2. Approval of 63 draft stories, artwork completion, real-device narration validation, full Art Studio parity, TV/Kids Corner and reward integrations.
3. Parent Corner production security hardening, accessibility and real-display/assistive-technology tests.
4. Native Linux, Windows and macOS builds, clean-system testing and installers.
5. Approved iMac-first synchronisation and website deployment **only after explicit authorisation**.
